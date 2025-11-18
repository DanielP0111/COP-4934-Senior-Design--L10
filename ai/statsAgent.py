from autogen import LLMConfig, ConversableAgent, UserProxyAgent
from baseAgent import BaseAgent
from tools.statTool import BMITool,pyTool, CodeExecutor


class StatAgent(BaseAgent):
    def __init__(self, executor: CodeExecutor):
        self.name = "StatAgent"
        self.description = "A statistics agent which calculates values based on user's requests."
        self.system_message = """
        You are a code executor agent for a healthcare facility.
        When a user asks for something you must write a full working python script to fufill their request and then pass this code to your pyTool tool.
        Ensure that this python script when ran will print the desired result so that the execution tool, pyTool, will be able to return that desired result.
        Once the python script is written, give the full python code to pyTool, which will execute the code and return it.
        Do not hallucinate or use your pretraining to answer the users question, you must use the tool's output to answer the user.
        ALWAYS write code to answer the users prompt and ALWAYS use pyTool to execute the code.
        
        Writing instructions that you must follow are these:
        First, do not write any comments in the python script.
        Second, write a print statement in the code for the desired result. Do not write any other print statements in the code besides this.
        Third, you need to always name the desired result's variable 'result' in the code.
        Fourth, ALWAYS verify the code was written properly to get the desired result for the user and so the other rules were followed exactly as described.
        
        Once you give the user the result from the tool, terminate the conversation and do not say anything until the user prompts you again.

        Repeat your last response until the user gives you a new instruction, asks a question, or any other non-empty response.
        """
        
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
    statAgent = StatAgent(CodeExecutor(timeout=10))
    statAgent.registerExecution(user_proxy)

    config = LLMConfig.from_json(path = "OAI_CONFIG_LIST.json")

    user_proxy.initiate_chat(
        statAgent.agent,
        message="My birthday is Novermber 22nd 2004, how many days have I been alive?",
        llm_config=config
    )
