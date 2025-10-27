# web parse tool that currently looks up drug prices
# from costplusdrugs

# fetches complete drug DB, caches, and matches

from typing import Dict, Any, Type, Optional, List
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
import requests
import json
from difflib import SequenceMatcher
from datetime import datetime, timedelta


# i am not sure how often this changes so i decided to cache the data for 24 hrs
# in case it does change. i can rework the logic around this and remove it entirely
# if it turns out we dont need it.

API_URL = "https://us-central1-costplusdrugs-publicapi.cloudfunctions.net/main"
CACHE_DURATION_HOURS = 24
_cached_drugs = None
_cache_timestamp = None

# fetches complete DB from the cost plus drugs API
# caches so API doesn't have to be called so much
# returns an array of drug objects with price info
# if API call fails requestException is raised

def fetch_drug_database() -> List[Dict[str, Any]]:
    global _cached_drugs, _cache_timestamp
    
    # is cache valid
    if _cached_drugs is not None and _cache_timestamp is not None:
        cache_age = datetime.now() - _cache_timestamp
        if cache_age < timedelta(hours=CACHE_DURATION_HOURS):
            print(f"using cached drug database ({len(_cached_drugs)} drugs)")
            return _cached_drugs
        
    # get new data
    print(f"fetching drug DB from {API_URL}...")
    try:
        response = requests.get(API_URL, timeout=30)
        response.raise_for_status()
        data = response.json()

        # get "results" array that API returns
        if isinstance(data, dict) and "results" in data:
            drugs = data["results"]
        elif isinstance(data, list):
            drugs = data
        else:
            raise ValueError("Unexpected API response format")
        
        _cached_drugs = drugs
        _cache_timestamp = datetime.now()
        print(f"successfully fetched {len(drugs)} drugs")
        return drugs
    
    except requests.RequestException as e:
        print(f"error fetching drug db: {e}")

        # return cached (possibly expired?) data if we have it to fall back on
        if _cached_drugs is not None:
            print(f"using possible old cached data as fallback.. ({len(_cached_drugs)} drugs)")
            return _cached_drugs
        
        raise

# calculate similiarity ratio using a sequence matcher library
# takes in 2 strings and returns a similarity ratio between 0.0 and 1.0
# this is for fuzzy matching for later
def calculate_similarity(str1: str, str2: str) -> float:
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

# search for drugs matching query string
# uses fuzzy matching (finding strings based on matching patterns and not identically)
# fuzzy matching handles variations in spelling/formatting of drug names
# searches medication_name field and ranks the results
# returns a list of matching drug objects with the best matching one first

def search_drugs(query: str, drugs: List[Dict[str, Any]], threshold: float = 0.6) -> List[Dict[str, Any]]:
    query_lower = query.lower().strip()
    matches = []

    for drug in drugs:
        med_name = drug.get("medication_name", "").lower()
        brand_name = drug.get("brand_name", "").lower()

        med_similarity = calculate_similarity(query_lower, med_name)
        brand_similarity = calculate_similarity(query_lower, brand_name) if brand_name else 0.0

        similarity = max(med_similarity, brand_similarity)

        if query_lower in med_name or query_lower in brand_name:
            similarity = max(similarity, 0.0)
        if similarity >= threshold:
            matches.append({
                "drug": drug,
                "similarity": similarity
            })
    
    matches.sort(key=lambda x: x["similarity"], reverse=True)
    return [match["drug"] for match in matches]

# formats the drug info cleanly for agent to take in
def format_drug_info(drug: Dict[str, Any]) -> Dict[str, Any]:
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

    # searches for drug prices
    def _run(self, drug_name: str, max_results: int = 5) -> Dict[str, Any]:
        print(f"searching for: {drug_name}...")
        try:
            drugs = fetch_drug_database()
            matches = search_drugs(drug_name, drugs, threshold=0.5)

            if not matches:
                return {
                    "found": False,
                    "query": drug_name,
                    "message": f"No medications found matching '{drug_name}'. Try a different spelling/generic name",
                    "results": []
                }

            matches = matches[:max_results]
            formatted_results = [format_drug_info(drug) for drug in matches]
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
    
# includes testing/debug stuff for now

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
