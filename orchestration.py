import asyncio
from autogen import AssistantAgent, UserProxyAgent,LLMConfig 
from autogen_agentchat.conditions import MaxMessageTermination, TextMessageTermination
from autogen_agentchat.messages import ChatMessage
from autogen_agentchat.base import Handoff
from autogen_agentchat.teams import Swarm
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
import os
from apiAgent import APIAgent
from dbAgent import DBAgent, DatabaseConnection

#pip install "autogen-ext[openai]"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ollama")
MODEL_BASE_URL = os.getenv("MODEL_BASE_URL", "http://localhost:11434/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:3b-instruct")

model_client = OpenAIChatCompletionClient(
    model=MODEL_NAME,
    api_key= OPENAI_API_KEY,
    base_url=MODEL_BASE_URL,
    model_info={
        "json_output": True, 
        "function_calling": True,  
        "vision": False,  
        "family": 'qwen2.5',  
        "structured_output": True  
    },
    parallel_tool_calls=False
)

dbAgent = DBAgent(DatabaseConnection)
apiAgent = APIAgent()
# Create the agents
orchestrator_agent = AssistantAgent(
    name="orchestrator",
    model_client=model_client,
    handoffs = [
        Handoff(target = dbAgent, description = 'When the users prompt is related to their personal healthcare data, medical history, appointments, or insurance provider.'),
        Handoff(target = apiAgent, description = 'When the users prompts are related to health tips, medical inquiries or advice')
        ], 
    system_message="""You are an orchestrator agent for a healthcare clinic application.
      Your task is to manage and coordinate the interactions between 
      the user and the other assistant agents. Any questions the user has about their insurance provider,
      medical history, or appointments should be directed to the dbAgent. Any questions about clinic services,
      health tips, or general medical inquiries should be directed to the apiAgent.
      """
)

termination = TextMessageTermination(source = orchestrator_agent) | MaxMessageTermination(max_messages=15)
team = Swarm(participants=[dbAgent, apiAgent,orchestrator_agent], termination_condition=termination)

async def run_team_stream(input: ChatMessage):
   return await Console(team.run_team_stream(task= input))
    

   
if __name__ == "__main__":    
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply= 1,
        code_execution_config={"use_docker": False},
    )

    # Initializes a class with an agent. Tool(s) are initialized inside.
    apiAgent = APIAgent()

    # Allows for the user_proxy to execute a tool(s)
    apiAgent.registerExecution(user_proxy)

    # This will become the JSON call once we fix that up.
    config = LLMConfig.from_json(path = "OAI_CONFIG_LIST.json")
    print("="*50)
    print("initializing database agent...")
    print("="*50)

    # init db connection (in this case for testing it's in-memory)
    print("\n1. setting up database connection...")
    db_connection = DatabaseConnection()

    # test db connection
    print("\n2. testing database connection...")
    db_connection.test_connection()

    # init the db agent
    print("\n4. initializing DBAgent...")
    db_agent = DBAgent(db_connection)

    # register tools for execution
    print("\n5. registering tools for execution...")
    db_agent.registerExecution(user_proxy)


    # Make sure to write .agent since apiAgent is a class object
    user_proxy.initiate_chat(
        apiAgent.agent,
        message="I would like to get some healthcare advice.",
        llm_config=config
    )
asyncio.run(run_team_stream())
