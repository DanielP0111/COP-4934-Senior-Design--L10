# web parse tool that currently looks up drug prices
# from costplusdrugs
# fetches complete drug DB, caches, and matches

from typing import Dict, Any, Type, Optional, List, ClassVar
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
import requests
import json
import copy
from difflib import SequenceMatcher
from datetime import datetime, timedelta
from bs4 import BeautifulSoup, Comment

# calculate similiarity ratio using a sequence matcher library
# takes in 2 strings and returns a similarity ratio between 0.0 and 1.0
# this is for fuzzy matching for later
def calculate_similarity(str1: str, str2: str) -> float:
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

class DrugPriceLookupArgs(BaseModel):
    drug_name: str = Field(..., description="Name of the medication to search for (for example, 'metformin' or 'lisinopril 10mg')")
    max_results: int = Field(5, description="Maximum number of results to return (default: 5)")

class DrugPriceLookupTool(BaseTool):
    name: str = "drug_price_lookup"
    description: str = (
        "Search for medication prices from Cost Plus Drugs. "
        "Provide the drug name (e.g., 'metformin', 'lisinopril 10mg') and get pricing information including "
        "strength, form, quantity, and cost. Returns multiple results if there are different formulations."
    )
    args_schema: Type[BaseModel] = DrugPriceLookupArgs

    # cache
    API_URL: ClassVar[str] = "https://us-central1-costplusdrugs-publicapi.cloudfunctions.net/main"
    CACHE_DURATION_HOURS: ClassVar[int] = 24
    _cached_drugs: ClassVar[Optional[List[Dict[str, Any]]]] = None
    _cache_timestamp: ClassVar[Optional[datetime]] = None

    def fetch_drug_database(self) -> List[Dict[str, Any]]:
        
        if self._cached_drugs is not None and self._cache_timestamp is not None:
            cache_age = datetime.now() - self._cache_timestamp
            if cache_age < timedelta(hours=self.CACHE_DURATION_HOURS):
                print(f"using cached drug database ({len(self._cached_drugs)} drugs)")
                return self._cached_drugs
            
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
    
    # search drugs using fuzzy matching
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
    
    def format_drug_info(self, drug: Dict[str, Any]) -> Dict[str, Any]:
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
    
# HTML parser tool
# parses HTML from any web page
class HTMLParserArgs(BaseModel):
    url: str = Field(..., description="URL of the webpage to parse (like 'http://example.com/blog')")
    extract_text: bool = Field(True, description="Extract all visible text content from the page (default: True)")
    extract_links: bool = Field(False, description="Extract all hyperlinks from the page (default: False)")
    extract_images: bool = Field(False, description="Extract all image sources from the page (default: False)")
    extract_scripts: bool = Field(False, description="Extract all script tags and their content (ATTACK VECTOR) (default: False)")
    extract_hidden: bool = Field(False, description="Extract hidden, invisible content like comments (ATTACK VECTOR) (default: False)")

class HTMLParserTool(BaseTool):
    name: str = "html_parser"
    description: str = (
        "Parse and extract content from any HTML webpage."
        "Retrieves text content, article titles, headings, and paragraphs"
        "Useful for reading anything HTML on the web."
        "Provide the URL to extract data in a structured form."
    )
    args_schema: Type[BaseModel] = HTMLParserArgs

    def _run(
        self,
        url: str,
        extract_text: bool = True,
        extract_links: bool = False,
        extract_images: bool = False,
        extract_scripts: bool = False,
        extract_hidden: bool = False
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
 
        soup_text = copy.copy(soup)
        
        # removes scripts, styles, meta, and link tags from the copied soup
        for element in soup_text(['script', 'style', 'meta', 'link']):
            element.decompose()

        #removes all hidden attributes
        for element in soup_text.select('[hidden]'):
            element.decompose()

        #removes all other attempts to hide text
        for element in soup_text.find_all(style=True):
            style = element['style'].replace(" ", "").lower()
            if any(keyword in style for keyword in [
                'display:none',
                'visibility:hidden',
                'opacity:0'
            ]):
                element.decompose()

        for element in soup_text.find_all(class_=True):
            classes = ' '.join(element['class']).lower()
            if any(keyword in classes for keyword in [
                'hidden',
                'invisible',
                'd-none',
                'hide'
            ]):
                element.decompose()
        # removes anything off screen
        for element in soup_text.find_all(style=True):
            style = element['style'].replace(" ", "").lower()

            if (
                "position:absolute" in style and
                any(keyword in style for keyword in [
                    "left:-",
                    "top:-",
                    "right:-",
                    "bottom:-"
                ])
            ):
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
    def _extract_hidden_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        hidden = {}

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
        #######################################################################
        # third method; find by hidden attributes ADDED FOR v2
        for element in soup.select('[hidden]'):
            print(element)
            text = element.get_text(strip=True)
            if text:
                hidden_elements.append({
                    "tag": element.name,
                    "text": text,
                    "attr": element['hidden']
                })
        #######################################################################
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
        extract_links: bool = False,
        extract_images: bool = False,
        extract_scripts: bool = False,
        extract_hidden: bool = False
    ) -> Dict[str, Any]:
        return self._run(url, extract_text, extract_links, extract_images, extract_scripts, extract_hidden)

