from autogen import LLMConfig, UserProxyAgent
from typing import List
from langchain.tools import BaseTool
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen.agentchat import ConversableAgent

def generate_llm_config(tool: BaseTool):
    args_schema = tool.args_schema.model_json_schema() if hasattr(tool, "args_schema") else {}
    function_schema = {
        "name": tool.name,
        "description": tool.description,
        "parameters": args_schema,
    }
    return {"function": function_schema}

class BaseAgent:
    def __init__(self, name: str, description: str, system_message: str, tools: List[BaseTool]):
        self.name = name
        self.description = description
        self.system_message = system_message
        self.tools = tools
        self.tools_config = self.getToolsConfig()
        self.config = self.getConfig()
        self.agent = self.createAgent()
    
    def getToolsConfig(self):
        tools_config = []
        for tool in self.tools:
            tools_config.append(generate_llm_config(tool))
            
        return tools_config

    def getConfig(self):
        config = LLMConfig(
            tools = self.tools_config,
            config_list = LLMConfig.from_json(path = "OAI_CONFIG_LIST.json").config_list,
            timeout = 120
        )

        return config
    
    def createAgent(self):
        return ConversableAgent(
            name = self.name,
            llm_config = self.config,
            system_message = self.system_message,
            max_consecutive_auto_reply = 3,
            #added to fix
            human_input_mode = "NEVER"
        )

    def registerExecution(self, user_proxy: UserProxyAgent):
        for tool in self.tools:
            def make_executor(t):
                return lambda **kwargs: t.invoke(kwargs)
        
            user_proxy.register_for_execution(
                name=tool.name,
            )(make_executor(tool))
