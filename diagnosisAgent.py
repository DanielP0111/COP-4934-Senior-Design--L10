from autogen import LLMConfig, UserProxyAgent
from baseAgent import BaseAgent
from tools.diagnosisApiTool import DiagnosisAPITool

class DiagnosisAgent(BaseAgent):
    def __init__(self):
        self.name = "DiagnosisAgent"
        self.description = "A diagnosis agent which collects and itemizes synonyms for diagnosis names."
        self.system_message = """
            You are a healthcare professional, specializing in giving users information about their diagonsis. 
            When prompted, you must use the DiagnosisAPITool tool to answer any question about a diagnosis. 
            Do not answer directly. Always use the tool first.
            Use the url https://clinicaltables.nlm.nih.gov/api/conditions/v3/search? as the baseUrl for the DiagnosisAPITool.
            When you use the tool, only return the output of the tool.
            After providing the answer, say 'TERMINATE' to end the conversation.
            
            "CONVERSATION PROTOCOL:"
            "1. Only speak when directly asked a question or when you have the specific information requested."
            "2. If another agent can handle the query, stay silent."
            "3. Default to silence unless you're certain your input is needed."
            """
        self.tools = [DiagnosisAPITool()]
        
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

    DiagnosisAgent = DiagnosisAgent()

    DiagnosisAgent.registerExecution(user_proxy)

    config = LLMConfig.from_json(path = "OAI_CONFIG_LIST.json")

    user_proxy.initiate_chat(
        DiagnosisAgent.agent,
        message="Could you tell me about the medicial condition called lupus?",
        llm_config=config
    )
