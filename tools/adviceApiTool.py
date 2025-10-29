from typing import Type, Optional
from pydantic import BaseModel, Field
from tools.baseApiTool import BaseAPIToolInput, BaseAPITool
import requests

class AdviceAPIToolInput(BaseAPIToolInput):
    baseUrl: str = Field(
        default="https://odphp.health.gov/myhealthfinder/api/v4/myhealthfinder.json?",
        description="Base URL for the API endpoint."
    )
    
    age: Optional[str] = Field(default=None, description="Age of the person. (Enter as a string)")
    sex: Optional[str] = Field(default=None, description="Sex of the person (male/female).")
    pregnant: Optional[str] = Field(default=None, description="Pregnancy status (yes/no).")
    sexuallyActive: Optional[str] = Field(default=None, description="Sexually active status (yes/no).")
    tobaccoUse: Optional[str] = Field(default=None, description="Tobacco use status (yes/no).")
    
class AdviceAPITool(BaseAPITool):
    name: str = "APITool"
    description: str = (
        "Use this tool when you need to access an API. "
        "Provide baseUrl (optional) and any of the following parameters: "
        "age, sex, pregnant, sexuallyActive, tobaccoUse."
    )
    args_schema: Type[BaseModel] = AdviceAPIToolInput

    def parse_response(self, response: requests.Response):
        data = response.json()
        try:
            return data['Result']['Resources']['All']['Resource'][0]['Sections']['section'][0]
        except Exception:
            return data

if __name__ == "__main__":
    apiTool = AdviceAPITool()

    query = AdviceAPIToolInput(
        age="35",
        sex="female",
        pregnant="no",
        sexuallyActive="yes",
        tobaccoUse="no"
    )

    result = apiTool._run(**query.model_dump())
    
    print(result)
