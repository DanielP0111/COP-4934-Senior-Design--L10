from autogen import AssistantAgent, LLMConfig, UserProxyAgent
from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from baseAgent import BaseAgent

# Activate the venv and run:
# pip install langchain langchain-community ag2[ollama]
# If you want to run this as main, follow the steps listed in the main file, currently named "autogen_try.py"

OPENAI_API_KEY = "ollama"

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
    return {"function": function_schema}

class APIAgent(BaseAgent):
    def __init__(self):
        self.name = "APIAgent"
        self.system_message = """
            You are a healthcare professional. When prompted, you must use the api_requester tool to answer any question
            about healthcare insurance providers. Do not answer directly. Always use the tool first. 
            When you use the tool, only return the output of the tool.
            """
        
        super().__init__(
            name = "APIAgent",
            system_message = self.system_message,
            tools = [APITool()]
        )

if __name__ == "__main__":    
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply= 1,
        code_execution_config={"use_docker": False},
    )

    # Initializes a class with an agent. Tool(s) are initialized inside.
    apiAgent = APIAgent()

    # Allows for the user_proxy to execute a tool(s)
    apiAgent.registerExecution(user_proxy)

    # This will become the JSON call once we fix that up.
    config = LLMConfig.from_json(path = "OAI_CONFIG_LIST.json")

    # Make sure to write .agent since apiAgent is a class object
    user_proxy.initiate_chat(
        apiAgent.agent,
        message="I need to get information about a healthcare insurance provider called United Healthcare.",
        llm_config=config
    )
