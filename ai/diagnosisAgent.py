from autogen import LLMConfig, UserProxyAgent
from baseAgent import BaseAgent
from tools.diagnosisApiTool import DiagnosisAPITool

class DiagnosisAgent(BaseAgent):
    def __init__(self, prompts):
        self.name = "DiagnosisAgent"
        self.description = prompts["descriptions"]
        self.system_message = prompts["instructions"]
        self.tools = [DiagnosisAPITool()]
        
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
        max_consecutive_auto_reply= 1,
        code_execution_config={"use_docker": False},
    )

    DiagnosisAgent = DiagnosisAgent()

    DiagnosisAgent.registerExecution(user_proxy)

    config = LLMConfig.from_json(path = "OAI_CONFIG_LIST.json")

    user_proxy.initiate_chat(
        DiagnosisAgent.agent,
        message="Could you tell me about the medicial condition called lupus?",
        llm_config=config
    )
