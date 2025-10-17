from autogen import LLMConfig, UserProxyAgent
from baseAgent import BaseAgent
from tools.apiTool import APITool

# Activate the venv and run:
# pip install langchain langchain-community ag2[ollama]
# If you want to run this as main, follow the steps listed in the main file, currently named "autogen_try.py"

class APIAgent(BaseAgent):
    def __init__(self):
        self.name = "APIAgent"
        self.system_message = """
            You are a healthcare professional. When prompted, you must use the APITool tool to answer any question
            about healthcare tips and advice. Do not answer directly. Always use the tool first.
            When you use the tool, only return the output of the tool.
            """
        
        super().__init__(
            name = self.name,
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

    apiAgent = APIAgent()

    apiAgent.registerExecution(user_proxy)

    config = LLMConfig.from_json(path = "OAI_CONFIG_LIST.json")

    user_proxy.initiate_chat(
        apiAgent.agent,
        message="I would like to get some healthcare advice. I am a 35 year old female, who is not pregnant, I am sexually active, and I do not smoke tobacco.",
        llm_config=config
    )
