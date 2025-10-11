from autogen import AssistantAgent, LLMConfig, UserProxyAgent
from typing import Optional, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool

# Activate the venv and run:
# pip install langchain langchain-community ag2[ollama]
# If you want to run this as main, follow the steps listed in the main file, currently named "autogen_try.py"

# Continue following: https://www.youtube.com/watch?v=ffG0zaYtOF4 around 2:14
class APIToolInput(BaseModel):
    request: str = Field()

class APITool(BaseTool):
    name: str = "api_requester"
    description: str = "Use this tool when you need to get information about a healthcare insurance provider."
    args_schema: Type[BaseModel] = APIToolInput
    
    def _run(self, request: str):
        print("API Tool has been used.")
        return "United Healthcare has been rated 'very good' by a professional doctor named Ted."

# This creates a pydantic dictionary "schema" that lets the agent understand its tool (easily scalable for many tools hopefully)
def generate_llm_config(tool):
    args_schema = tool.args_schema.model_json_schema() if hasattr(tool, "args_schema") else {}
    function_schema = {
        "name": tool.name,
        "description": tool.description,
        "parameters": args_schema,
    }
    return function_schema

class APIAgent:
    def __init__(self, config):
        self.agent = AssistantAgent(
            name="API Agent",
            llm_config = config,
            system_message="""
            You are a healthcare professional. When prompted, you must use the api_requester tool to answer any question
            about healthcare insurance providers. Do not answer directly. Always use the tool first.
            """,
        )

if __name__ == "__main__":
    api_tool = APITool()
    
    # Can do multiple functions. Maybe for different API endpoints I do different functions?
    llm_config = LLMConfig(
        tools = [
            generate_llm_config(api_tool),
        ],
        # Doing this instead of calling the json because that method is depreciated.
        config_list = [
            {
                "model": "qwen2.5:3b",
                "api_type": "ollama",
                "base_url": "http://localhost:11434",
                "temperature": 0.3
                
            }
        ],
        timeout = 120,
    )
    
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="ALWAYS",
        max_consecutive_auto_reply= 1,
        code_execution_config={"work_dir": "coding",
                            "use_docker": False},
    )

    user_proxy.register_function(
        function_map={
            api_tool.name: api_tool._run,
        }
    )

    # Note the .agent at the end. This references the agent in the wrapper so no class annoyingness happens after its passed.
    apiAgent = APIAgent(llm_config).agent

    user_proxy.initiate_chat(
        apiAgent,
        message="I need to get information about a healthcare insurance provider called United Healthcare.",
        llm_config=llm_config
    )
