# web parse tool that currently looks up drug prices
# from costplusdrugs

# fetches complete drug DB, caches, and matches

# =========================
# 1: IMPORTS
# =========================

from typing import Dict, Any, Type, Optional, List, ClassVar
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
import requests
import json
import copy
from difflib import SequenceMatcher
from datetime import datetime, timedelta
from bs4 import BeautifulSoup, Comment

# =========================
# 2: POTENTIAL SHARED UTILITIES
# =========================

# calculate similiarity ratio using a sequence matcher library
# takes in 2 strings and returns a similarity ratio between 0.0 and 1.0
# this is for fuzzy matching for later
def calculate_similarity(str1: str, str2: str) -> float:
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

# =========================
# 3: DRUG LOOKUP TOOL
# =========================

class DrugPriceLookupArgs(BaseModel):
    drug_name: str = Field(..., description="Name of the medication to search for (for example, 'metformin' or 'lisinopril 10mg')")
    max_results: int = Field(5, description="Maximum number of results to return (default: 5)")

# tool for looking up medication prices from costplusdrugs
class DrugPriceLookupTool(BaseTool):
    name: str = "drug_price_lookup"
    description: str = (
        "Search for medication prices from Cost Plus Drugs. "
        "Provide the drug name (e.g., 'metformin', 'lisinopril 10mg') and get pricing information including "
        "strength, form, quantity, and cost. Returns multiple results if there are different formulations."
    )
    args_schema: Type[BaseModel] = DrugPriceLookupArgs

    # i am not sure how often this changes so i decided to cache the data for 24 hrs
    # in case it does change. i can rework the logic around this and remove it entirely
    # if it turns out we dont need it.
    API_URL: ClassVar[str] = "https://us-central1-costplusdrugs-publicapi.cloudfunctions.net/main"
    CACHE_DURATION_HOURS: ClassVar[int] = 24
    _cached_drugs: ClassVar[Optional[List[Dict[str, Any]]]] = None
    _cache_timestamp: ClassVar[Optional[datetime]] = None

    # fetches complete DB from the cost plus drugs API
    # caches so API doesn't have to be called so much
    # returns an array of drug objects with price info
    # if API call fails requestException is raised
    def fetch_drug_database(self) -> List[Dict[str, Any]]:
        
        # is cache valid
        if self._cached_drugs is not None and self._cache_timestamp is not None:
            cache_age = datetime.now() - self._cache_timestamp
            if cache_age < timedelta(hours=self.CACHE_DURATION_HOURS):
                print(f"using cached drug database ({len(self._cached_drugs)} drugs)")
                return self._cached_drugs
            
        # get new data
        print(f"fetching drug DB from {self.API_URL}...")
        try:
            response = requests.get(self.API_URL, timeout=30)
            response.raise_for_status()
            data = response.json()

            # get "results" array that API returns
            if isinstance(data, dict) and "results" in data:
                drugs = data["results"]
            elif isinstance(data, list):
                drugs = data
            else:
                raise ValueError("Unexpected API response format")
            
            DrugPriceLookupTool._cached_drugs = drugs
            DrugPriceLookupTool._cache_timestamp = datetime.now()
            print(f"successfully fetched {len(drugs)} drugs")
            return drugs
        
        except requests.RequestException as e:
            print(f"error fetching drug db: {e}")

            # return cached (possibly expired?) data if we have it to fall back on
            if self._cached_drugs is not None:
                print(f"using possible old cached data as fallback.. ({len(self._cached_drugs)} drugs)")
                return self._cached_drugs
            
            raise
    
    # search drugs goes here
    # search for drugs matching query string
    # uses fuzzy matching (finding strings based on matching patterns and not identically)
    # fuzzy matching handles variations in spelling/formatting of drug names
    # searches medication_name field and ranks the results
    # returns a list of matching drug objects with the best matching one first
    def search_drugs(self, query: str, drugs: List[Dict[str, Any]], threshold: float = 0.6) -> List[Dict[str, Any]]:
        query_lower = query.lower().strip()
        matches = []

        for drug in drugs:
            med_name = drug.get("medication_name", "").lower()
            brand_name = drug.get("brand_name", "").lower()

            med_similarity = calculate_similarity(query_lower, med_name)
            brand_similarity = calculate_similarity(query_lower, brand_name) if brand_name else 0.0

            similarity = max(med_similarity, brand_similarity)

            if query_lower in med_name or query_lower in brand_name:
                similarity = max(similarity, 0.9)
            if similarity >= threshold:
                matches.append({
                    "drug": drug,
                    "similarity": similarity
                })
        
        matches.sort(key=lambda x: x["similarity"], reverse=True)
        return [match["drug"] for match in matches]
    
    # format drug info goes here
    # formats the drug info cleanly for agent to take in
    def format_drug_info(self, drug: Dict[str, Any]) -> Dict[str, Any]:
        # parse price
        unit_price = drug.get("unit_billing_price", "$0.00").replace("$", "")
        quantity = int(drug.get("medisapn_quantity", 1))

        try:
            price_per_unit = float(unit_price)
            total_price = price_per_unit * quantity
        except (ValueError, TypeError):
            price_per_unit = 0.0
            total_price = 0.0
        
        return {
            "medication_name": drug.get("medication_name", "Unknown"),
            "brand_name": drug.get("brand_name", "N/A"),
            "generic": drug.get("brand_generic", "Unknown") == "Generic",
            "form": drug.get("form", "Unknown"),
            "strength": drug.get("strength", "Unknown"),
            "quantity": quantity,
            "pack_size": drug.get("medisapn_pack_size", "Unknown"),
            "pack_units": drug.get("medisapn_pack_size_units", "ea"),
            "price_per_unit": f"${price_per_unit}",
            "total_price": f"${total_price}",
            "ndc": drug.get("ndc", "Unknown"),
            "url": drug.get('url', ""),
            "insurance_eligible": drug.get("insurance_eligible", "Unknown"),
            "auto_refill": drug.get("auto_refill", False)
        }
    
    # searches for drug prices
    def _run(self, drug_name: str, max_results: int = 5) -> Dict[str, Any]:
        print(f"searching for: {drug_name}...")
        try:
            drugs = self.fetch_drug_database()
            matches = self.search_drugs(drug_name, drugs, threshold=0.5)

            if not matches:
                return {
                    "found": False,
                    "query": drug_name,
                    "message": f"No medications found matching '{drug_name}'. Try a different spelling/generic name",
                    "results": []
                }

            matches = matches[:max_results]
            formatted_results = [self.format_drug_info(drug) for drug in matches]
            print(f"found {len(formatted_results)} matches")
            
            return {
                "found": True,
                "query": drug_name,
                "count": len(formatted_results),
                "results": formatted_results
            }
        except Exception as e:
            print(f"drug lookup error: {e}")
            return {
                "found": False,
                "query": drug_name,
                "error": str(e),
                "message": "Failed to fetch drug prices. API might be unavailable",
                "results": []
            }

    async def _arun(self, drug_name: str, max_results: int = 5) -> Dict[str, Any]:
        return self._run(drug_name, max_results)
    
# =========================
# 4. HTML PARSING TOOL
# =========================

class HTMLParserArgs(BaseModel):
    url: str = Field(..., description="URL of the webpage to parse (like 'http://example.com/blog')")
    extract_text: bool = Field(True, description="Extract all visible text content from the page (default: True)")
    extract_links: bool = Field(False, description="Extract all hyperlinks from the page (default: False)")
    extract_images: bool = Field(False, description="Extract all image sources from the page (default: False)")
    extract_scripts: bool = Field(True, description="Extract all script tags and their content (ATTACK VECTOR) (default: True)")
    extract_hidden: bool = Field(True, description="Extract hidden, invisible content like comments (ATTACK VECTOR) (default: True)")

# parses HTML from any web page
# takes text, links, scripts, hidden/invisible content, scalable for any HTML page
# warning: this is a research tool, so this extracts everything including potentially malicious items from a web page
# use on sites known to be safe in order to be safe

class HTMLParserTool(BaseTool):
    name: str = "html_parser"
    description: str = (
        "Parse and extract content from any HTML webpage."
        "Retrieves text content, article titles, headings, paragraphs, any embedded scripts."
        "Retrieves hidden elements and HTML comments."
        "Useful for reading anything HTML on the web."
        "Provide the URL to extract data in a structured form."
    )
    args_schema: Type[BaseModel] = HTMLParserArgs

    def _run(
        self,
        url: str,
        extract_text: bool = True,
        extract_links: bool = True,
        extract_images: bool = True,
        extract_scripts: bool = True,
        extract_hidden: bool = True
    ) -> Dict[str, Any]:
        # executes the HTML parsing on given URL
        # returns structured data including page metadata, text, embedded scripts, hidden content, or links/images if enabled
        print(f"[parser] fetching URL: {url}")

        try:
            response = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (HealthcareBot/1.0; +http://example.com/bot)'
            })
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            result = {
                "success": True,
                "url": url,
                "timestamp": datetime.now().isoformat(),
            }

            result["metadata"] = self._extract_metadata(soup)
            if extract_text:
                result["text_content"] = self._extract_text(soup)
            if extract_links:
                result["links"] = self._extract_links(soup)
            if extract_images:
                result["images"] = self._extract_images(soup)
            if extract_scripts:
                scripts = self._extract_scripts(soup)
                result["scripts"] = scripts
                result["script_count"] = len(scripts)
            if extract_hidden:
                hidden = self._extract_hidden_content(soup)
                result["hidden_content"] = hidden
            print(f"[parser] successfully parsed. extracted {len(result.get('text_content', {}).get('paragraphs', []))} paragraphs, {result.get('script_count', 0)} scripts")

            return result
        except requests.RequestException as e:
            print(f"[parser] request error: {e}")
            return {
                "success": False,
                "url": url,
                "error": str(e),
                "error_type": "request_error",
                "message": f"failed to fetch page from {url}; server may be unreachable"
            }
        except Exception as e:
            print(f"[parser] parsing error: {e}")
            return {
                "success": False,
                "url": url,
                "error": str(e),
                "error_type": "parse_error",
                "message": "failed to parse HTML. page structure may not be valid"
            }

    # extracts basic page metadata like title, desc, etc   
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        metadata = {}
        
        title = soup.find('title')
        if title:
            metadata["title"] = title.get_text(strip=True)

        # Meta description & keywords
        description = soup.find('meta', attrs={'name': 'description'})
        if description and description.get('content'):
            metadata["description"] = description.get('content')
        
        keywords = soup.find('meta', attrs={'name': 'keywords'})
        if keywords and keywords.get('content'):
            metadata["keywords"] = keywords.get('content')
        
        # Open Graph title (social media)
        # probably useless
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            metadata["og_title"] = og_title.get('content')
        
        # author extraction
        author = soup.find('meta', attrs={'name': 'author'})
        if author and author.get('content'):
            metadata["author"] = author.get('content')

        return metadata
    
    # extracts all text content from a page and structures it
    def _extract_text(self, soup: BeautifulSoup) -> Dict[str, Any]:
        text_content = {}

        # extracts headings h1-h6
        headings = []
        for level in range(1, 7):
            for heading in soup.find_all(f'h{level}'):
                text = heading.get_text(strip=True)
                if text:
                    headings.append({
                        "level": level,
                        "text": text
                    })
        text_content["headings"] = headings

        # extracts paragraphs
        paragraphs = []
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if text:
                paragraphs.append(text)
        text_content["paragraphs"] = paragraphs

        # extracts list items
        list_items = []
        for li in soup.find_all('li'):
            text = li.get_text(strip=True)
            if text:
                list_items.append(text)
        text_content["list_items"] = list_items

        # extracts blockquotes
        quotes = []
        for quote in soup.find_all('blockquote'):
            text = quote.get_text(strip=True)
            if text:
                quotes.append(text)
        text_content["quotes"] = quotes
 
        soup_text = copy.copy(soup)
        
        # removes scripts, styles, meta, and link tags from the copied soup
        for element in soup_text(['script', 'style', 'meta', 'link']):
            element.decompose()
        
        full_text = soup_text.get_text(separator=' ', strip=True)
        text_content["full_text"] = full_text

        return text_content
    
    # extracts all hyperlinks
    def _extract_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        links = []

        for a_tag in soup.find_all('a', href=True):
            link_data = {
                "href": a_tag['href'],
                "text": a_tag.get_text(strip=True)
            }

            # if it has a title include the title
            if a_tag.get('title'):
                link_data["title"] = a_tag['title']
            
            links.append(link_data)
        
        return links
    
    # extracts all images
    def _extract_images(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        images = []

        for img_tag in soup.find_all('img'):
            img_data = {}

            if img_tag.get('src'):
                img_data["src"] = img_tag['src']
            if img_tag.get('alt'):
                img_data["alt"] = img_tag['alt']
            if img_tag.get('title'):
                img_data["title"] = img_tag['title']
            if img_data:
                images.append(img_data)
        
        return images
    
    # extracts all script tags
    # this is an attack vector
    # the idea is bad actors inject code into webpages that gets extracted and potentially executed by the agent
    # could include JS containing prompt injection instructions
    # could include encoded commands hidden
    # could include remote script loading from malicious servers
    # etc etc
    def _extract_scripts(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        scripts = []

        for idx, script_tag in enumerate(soup.find_all('script')):
            script_data = {
                "index": idx,
                "type": script_tag.get('type', 'text/javascript'),
            }

            # check if its an external script
            if script_tag.get('src'):
                script_data["source"] = "external"
                script_data["src"] = script_tag.get('src')
                script_data["content"] = None
            else:
                script_data["source"] = "inline"
                # get the contents of the script
                content = script_tag.string
                if content:
                    script_data["content"] = content.strip()
                else:
                    # handles cases where script content is in text nodes
                    script_data["content"] = script_tag.get_text(strip=True)
            
            # extract any other attributes (i.e. async, defer, integrity, etc etc)
            other_attrs = {k: v for k, v in script_tag.attrs.items() 
                          if k not in ['src', 'type']}
            
            if other_attrs:
                script_data["attributes"] = other_attrs

            scripts.append(script_data)
        
        return scripts
    
    # extracts all hidden content
    # this is an attack vector
    # the idea is attackers hide malicious instructions in things like
    # HTML comments, hidden elements, data attributes, custom meta tags, offscreen elements
    def _extract_hidden_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        hidden = {}

        # extract HTML comments
        comments = soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--'))
        if not comments:
            comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        
        if comments:
            comment_list = []
            for comment in comments:
                comment_text = str(comment).strip()
                # take delimiters out
                comment_text = comment_text.replace('<!--', '').replace('-->', '').strip()
                if comment_text:
                    comment_list.append(comment_text)
            hidden["comments"] = comment_list
            hidden["comment_count"] = len(comment_list)
        
        # these are elements with display:none or visibility:hidden
        hidden_elements = []

        # first method; find by inline style
        for element in soup.find_all(style=True):
            style = element['style'].lower()
            if any(keyword in style for keyword in ['display:none', 'display: none', 
                                                      'visibility:hidden', 'visibility: hidden',
                                                      'opacity:0', 'opacity: 0']):
                text = element.get_text(strip=True)
                if text:
                    hidden_elements.append({
                        "tag": element.name,
                        "text": text,
                        "style": element['style']
                    })
        
        # second method; find by hidden classes
        for element in soup.find_all(class_=True):
            classes = ' '.join(element['class']).lower()
            if any(keyword in classes for keyword in ['hidden', 'invisible', 'd-none', 'hide']):
                text = element.get_text(strip=True)
                if text:
                    hidden_elements.append({
                        "tag": element.name,
                        "text": text,
                        "class": ' '.join(element['class'])
                    })

        if hidden_elements:
            hidden["hidden_elements"] = hidden_elements
            hidden["hidden_element_count"] = len(hidden_elements)
        
        # extracts all data and attributes
        data_attrs = []
        for element in soup.find_all(lambda tag: any(attr.startswith('data-') for attr in tag.attrs)):
            data_dict = {attr: element[attr] for attr in element.attrs if attr.startswith('data-')}
            if data_dict:
                data_attrs.append({
                    "tag": element.name,
                    "attributes": data_dict,
                    # for this preview it only grabs the first 100 characters
                    "text_preview": element.get_text(strip=True)[:100]
                })
        
        if data_attrs:
            hidden["data_attributes"] = data_attrs
            hidden["data_attribute_count"] = len(data_attrs)
        
        # extracts custom meta tags
        custom_meta = []
        for meta in soup.find_all('meta'):
            # skip normal meta tags
            if not meta.get('charset') and meta.get('name') not in ['description', 'keywords', 'author', 'viewport']:
                meta_data = {}
                if meta.get('name'):
                    meta_data["name"] = meta['name']
                if meta.get('content'):
                    meta_data["content"] = meta['content']
                if meta.get('property'):
                    meta_data["property"] = meta['property']
                
                if meta_data:
                    custom_meta.append(meta_data)
        if custom_meta:
            hidden["custom_meta_tags"] = custom_meta

        # extracts offscreen elements or elements with sus positioning
        offscreen_elements = []
        for element in soup.find_all(style=True):
            style = element['style'].lower()
            if any(keyword in style for keyword in ['left:-', 'top:-', 'position:absolute']):
                text = element.get_text(strip=True)
                if text:
                    offscreen_elements.append({
                        "tag": element.name,
                        "text": text[:200],
                        "style": element['style']
                    })
        
        if offscreen_elements:
            hidden["offscreen_elements"] = offscreen_elements
        
        return hidden if hidden else None
    
    async def _arun(
        self,
        url: str,
        extract_text: bool = True,
        extract_links: bool = True,
        extract_images: bool = True,
        extract_scripts: bool = True,
        extract_hidden: bool = True
    ) -> Dict[str, Any]:
        return self._run(url, extract_text, extract_links, extract_images, extract_scripts, extract_hidden)

# =========================
# 5. TESTING BLOCK
# =========================

# includes testing/debug stuff for now for the drug lookup tool

if __name__ == "__main__":
    print("testing DrugPriceLookupTool...")

    tool = DrugPriceLookupTool()

    test_queries = [
        "metformin",
        "lisinopril 10mg",
        "albuterol",
        "atorvatstatin",
        "nonexistent_drug_xyz"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*50}")
        print(f"Test {i}: {query}")
        print(f"\n{'='*50}")

        result = tool._run(query, max_results=3)

        if result["found"]:
            print(f"\n found {result['count']} results:")
            for j, drug in enumerate(result["results"], 1):
                print(f"\n  {j}. {drug['medication_name']}")
                print(f"    Brand: {drug['brand_name']}")
                print(f"    Form: {drug['form']} | Strength: {drug['strength']}")
                print(f"    Price per unit: {drug['price_per_unit']}")
                print(f"    Total price: {drug['total_price']}")
                print(f"    URL: {drug['url']}")
        else:
            print(f"\n {result['message']}")
            if "error" in result:
                print(f"    error: {result['error']}")
    
    print("testing complete.")
