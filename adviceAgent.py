from autogen import LLMConfig, UserProxyAgent
from baseAgent import BaseAgent
from tools.adviceApiTool import AdviceAPITool

# Activate the venv and run:
# pip install langchain langchain-community ag2[ollama]
# If you want to run this as main, follow the steps listed in the main file, currently named "autogen_try.py"

class AdviceAgent(BaseAgent):
    def __init__(self):
        self.name = "AdviceAgent"
        self.system_message = """
            You are a healthcare professional, specializing in giving users advice. When prompted, you must use the AdviceAPITool tool to answer any question
            about healthcare tips and advice. Do not answer directly. Always use the tool first.
            Use the url https://odphp.health.gov/myhealthfinder/api/v4/myhealthfinder.json? as the baseUrl for the AdviceAPITool.
            When you use the tool, only return the output of the tool.
            After providing the answer, say 'TERMINATE' to end the conversation.
            
            "CONVERSATION PROTOCOL:"
            "1. Only speak when directly asked a question or when you have the specific information requested."
            "2. If another agent can handle the query, stay silent."
            "3. Default to silence unless you're certain your input is needed."
            """
        self.tools = [AdviceAPITool()]
        
        super().__init__(
            name = self.name,
            system_message = self.system_message,
            tools = self.tools
        )

if __name__ == "__main__":    
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply= 1,
        code_execution_config={"use_docker": False},
    )

    AdviceAgent = AdviceAgent()

    AdviceAgent.registerExecution(user_proxy)

    config = LLMConfig.from_json(path = "OAI_CONFIG_LIST.json")

    user_proxy.initiate_chat(
        AdviceAgent.agent,
        message="I would like to get some healthcare advice. I am a 35 year old female, who is not pregnant, I am sexually active, and I do not smoke tobacco.",
        llm_config=config
    )
