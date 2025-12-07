from autogen import LLMConfig, UserProxyAgent
from baseAgent import BaseAgent
from tools.adviceApiTool import AdviceAPITool
from tools.webParseTool import HTMLParserTool

# Activate the venv and run:
# pip install langchain langchain-community ag2[ollama]
# If you want to run this as main, follow the steps listed in the main file, currently named "autogen_try.py"

class AdviceAgent(BaseAgent):
    def __init__(self, prompts):
        self.name = "AdviceAgent"
        self.description = prompts["descriptions"]
        self.system_message = prompts["instructions"]
        self.tools = [AdviceAPITool(), HTMLParserTool()]
        
        super().__init__(
            name = self.name,
            description = self.description,
            system_message = self.system_message,
            tools = self.tools
        )

if __name__ == "__main__":    
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply= 5,
        code_execution_config={"use_docker": False},
    )

    AdviceAgent = AdviceAgent()

    AdviceAgent.registerExecution(user_proxy)

    config = LLMConfig.from_json(path = "OAI_CONFIG_LIST.json")

    user_proxy.initiate_chat(
        AdviceAgent.agent,
        message="I would like to get some healthcare advice. I am a 35 year old female, who is not pregnant, I am sexually active, and I do not smoke tobacco.",
    #    message="Can you check the health blog at http://tedmed/index.html and tell me what health advice it recommends?",
        llm_config=config
    )
