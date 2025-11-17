from typing import Dict, Any, Type, Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
import requests

# pip install requests

class BaseAPIToolInput(BaseModel):
    baseUrl: str = Field(
        default=None,
        description="Base URL for the API endpoint."
    )

class BaseAPITool(BaseTool):
    name: str = "BaseAPITool"
    description: str = "Use this tool when you need to access an API."
    args_schema: Type[BaseModel] = BaseAPIToolInput

    def build_params(self, query: BaseModel) -> Dict[str, Any]:
        return {
            k: v for k, v in query.model_dump().items()
            if k != "baseUrl" and v is not None
        }

    def parse_response(self, response: requests.Response) -> Any:
        return response.json()

    def _run(self, **kwargs):
        try:
            query = self.args_schema(**kwargs)
            params = self.build_params(query)

            response = requests.get(query.baseUrl, params=params, timeout=10)            
            response.raise_for_status()
            return self.parse_response(response)
        except requests.exceptions.RequestException as e:
            return {"Error": str(e)}
