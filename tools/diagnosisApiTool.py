from typing import Type, Optional
from pydantic import BaseModel, Field
from tools.apiTool import BaseAPIToolInput, BaseAPITool
import requests

class DiagnosisAPIToolInput(BaseAPIToolInput):
    baseUrl: str = Field(
        default="https://clinicaltables.nlm.nih.gov/api/conditions/v3/search?",
        description="Base URL for the API endpoint."
    )
    
    terms: str = Field(
            default=None,
            description="The search string (e.g., just a part of a word) for which to find matches in the list. More than one partial word can be present in 'terms', in which case there is an implicit AND between them."
        )
    
class DiagnosisAPITool(BaseAPITool):
    name: str = "DiagnosisAPITool"
    description: str = (
        "Use this tool when you need to access an API. "
        "Provide baseUrl (optional) and any of the following parameters: "
        "terms."
    )
    args_schema: Type[BaseModel] = DiagnosisAPIToolInput

if __name__ == "__main__":
    apiTool = DiagnosisAPITool()

    query = DiagnosisAPIToolInput(
        baseUrl="https://clinicaltables.nlm.nih.gov/api/conditions/v3/search?",
        terms="Cough",
    )

    result = apiTool._run(**query.model_dump())
    
    print(result)
