from typing import Dict, Any, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
import requests

# pip install requests

class APIToolInput(BaseModel):
    baseUrl: str = Field()
    params: Dict[str, Any] = Field(default_factory=dict)

class APITool(BaseTool):
    name: str = "APITool"
    description: str = "Use this tool when you need to access an API. baseURL is for the API's base url and params is a dictionary of parameters."
    args_schema: Type[BaseModel] = APIToolInput
    
    def _run(self, query: APIToolInput):
        try:
            response = requests.get(query.baseUrl, params = query.params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"Error": str(e)}

if __name__ == "__main__":
    apiTool = APITool()
    
    baseUrl = "https://odphp.health.gov/myhealthfinder/api/v4/myhealthfinder.json?"
    params = {"age": "35", "sex": "female", "pregnant": "no", "sexuallyActive": "yes", "tobaccoUse": "no"}
    
    query = APIToolInput(baseUrl = baseUrl, params = params)
    
    result = apiTool._run(query)['Result']
    resources = result['Resources']['All']['Resource']
    
    # This prints what this Resource is about.
    print(resources[0]['Title'])
    print("\n")
    
    sections = resources[0]['Sections']['section']
    
    # Prints out Title and Content of the first resource
    for i in range(len(sections)):
        print(sections[i])
        print("\n\n")
