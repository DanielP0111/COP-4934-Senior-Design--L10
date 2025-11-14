from autogen import LLMConfig, ConversableAgent, UserProxyAgent
from baseAgent import BaseAgent
from tools.statTool import BMITool,pyTool, CodeExecutor


class StatAgent(BaseAgent):
    def __init__(self, executor: CodeExecutor):
        self.name = "StatAgent"
        self.system_message = """
        You are a code executor statistics agent for a healthcare facility.
          Use the BMI tool when a user provides their height and weight"""
        
        super().__init__(
            name = self.name,
            system_message = self.system_message,
            tools = [BMITool(),pyTool()]
        )
        

if __name__ == "__main__":    

    user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2,
            code_execution_config={"use_docker": False},
        )
    statAgent = StatAgent(CodeExecutor(timeout=10))
    statAgent.registerExecution(user_proxy)

    config = LLMConfig.from_json(path = "OAI_CONFIG_LIST.json")

    user_proxy.initiate_chat(
        statAgent.agent,
        message="Write Python code that computes the Fibonacci sequence up to 20, run it, and show the result.",
        llm_config=config
    )




   
