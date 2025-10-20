from typing import Dict, Any, Type, Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
import requests

# pip install requests

class APIToolInput(BaseModel):
    baseUrl: str = Field(
        default="https://odphp.health.gov/myhealthfinder/api/v4/myhealthfinder.json?",
        description="Base URL for the API endpoint."
    )
    age: Optional[str] = Field(default=None, description="Age of the person. (Enter as a string)")
    sex: Optional[str] = Field(default=None, description="Sex of the person (male/female).")
    pregnant: Optional[str] = Field(default=None, description="Pregnancy status (yes/no).")
    sexuallyActive: Optional[str] = Field(default=None, description="Sexually active status (yes/no).")
    tobaccoUse: Optional[str] = Field(default=None, description="Tobacco use status (yes/no).")

class APITool(BaseTool):
    name: str = "APITool"
    description: str = (
        "Use this tool when you need to access an API. "
        "Provide baseUrl (optional) and any of the following parameters: "
        "age, sex, pregnant, sexuallyActive, tobaccoUse."
    )
    args_schema: Type[BaseModel] = APIToolInput
    
    def _run(self, **kwargs):
        try:
            query = APIToolInput(**kwargs)
            params = {}
            for key, value in query.dict().items():
                if key == "baseUrl":
                    continue 
                if value is not None:
                    params[key] = value

            response = requests.get(query.baseUrl, params=params, timeout=10)            
            response.raise_for_status()
            
            # The first resource, with many articles about that subject. Currently hardcoded, will fix when I have a better idea.
            result = response.json()['Result']['Resources']['All']['Resource'][0]['Sections']['section'][0]
            
            return result
        except requests.exceptions.RequestException as e:
            return {"Error": str(e)}

if __name__ == "__main__":
    apiTool = APITool()

    query = APIToolInput(
        age="35",
        sex="female",
        pregnant="no",
        sexuallyActive="yes",
        tobaccoUse="no"
    )

    result = apiTool._run(**query.dict())
    
    sections = result['Sections']['section']
    
    # Prints out Title and Content of the first resource
    for i in range(len(sections)):
        print(sections[i])
        print("\n\n")
