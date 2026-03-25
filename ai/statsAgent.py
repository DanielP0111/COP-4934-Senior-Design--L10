from autogen import LLMConfig, ConversableAgent, UserProxyAgent
from baseAgent import BaseAgent
from tools.statTool import DockerCodeExecutor


class StatAgent(BaseAgent):
    def __init__(self, executor: DockerCodeExecutor, prompts):
        self.name = "StatAgent"
        self.description = prompts["descriptions"]
        self.system_message = prompts["instructions"]
        
        super().__init__(
            name = self.name,
            description = self.description,
            system_message = self.system_message,
            tools = [pyTool()]
        )
        

if __name__ == "__main__":    

    user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2,
            code_execution_config={"use_docker": False},
        )
    statAgent = StatAgent(DockerCodeExecutor(timeout=10))
    statAgent.registerExecution(user_proxy)

    config = LLMConfig.from_json(path = "OAI_CONFIG_LIST.json")

    user_proxy.initiate_chat(
        statAgent.agent,
        message="My birthday is Novermber 22nd 2004, how many days have I been alive?",
        llm_config=config
    )
