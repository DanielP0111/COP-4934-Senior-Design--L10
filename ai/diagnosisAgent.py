from autogen import LLMConfig, UserProxyAgent
from baseAgent import BaseAgent
from tools.diagnosisApiTool import DiagnosisAPITool

class DiagnosisAgent(BaseAgent):
    def __init__(self):
        self.name = "DiagnosisAgent"
        self.description = "A diagnosis agent which collects and itemizes synonyms for diagnosis names."
        self.system_message = """
            You are a healthcare professional specializing in providing specific information about MEDICAL CONDITIONS and DISEASES.

            YOUR SCOPE (You ONLY handle these topics):
                - Specific medical conditions (lupus, diabetes, arthritis, etc.)
                - Disease information and definitions
                - Symptoms of specific conditions
                - Questions like "What is (disease)?" or "Tell me about (condition)"
                - Any query containg a question about a specific medical condition

            When prompted about ANY medical condition or disease, you MUST use the DiagnosisAPITool to answer.
            Do NOT answer directly. Always use the tool first.

            Use the URL https://clinicaltables.nlm.nih.gov/api/conditions/v3/search? as the baseUrl for the DiagnosisAPITool.
            Do NOT make up or hallucinate any other URLs, or attempt to use the DiagnosisAPITool tool with any other URL.
            
            When you use the tool, provide a clear summary of the information found.

            EXAMPLES:
                Examples of queries you should handle:
                - "Tell me about lupus"
                - "What is diabetes?"
                - "Could you tell me about the medical condition called lupus?"
                - "Information about arthritis"

            CONVERSATION PROTOCOL:
                1. If the query is about a SPECIFIC medical disease or condition: Use DiagnosisAPITool immediately
                2. If the query is about general health advice or prevention: stay SILENT, another agent can handle this
                3. ALWAYS use the tool before responding; do NOT hallucinate ANY information
                4. Provide clear, concise information based on the output of the DiagnosisAPITool used.

            After providing the answer, say 'TERMINATE' to signify the end of the conversation.
            """
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
