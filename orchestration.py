import asyncio
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent 
from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination
from autogen_agentchat.messages import HandoffMessage
from autogen_agentchat.teams import Swarm
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
import os

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


# Create the agents
orchestrator_agent = AssistantAgent(
    name="orchestrator",
    model_client=model_client,
    handoffs = ["dbAgent", "apiAgent","user"], # can handoff to user if more info needed
    system_message="""You are an orchestrator agent for a healthcare clinic application.
      Your task is to manage and coordinate the interactions between 
      the user and the other assistant agents. Any questions the user has about their insurance provider,
      medical history, or appointments should be directed to the dbAgent. Any questions about clinic services,
      health tips, or general medical inquiries should be directed to the apiAgent.
      """
)

#example db agent to test handoff and swarm functionality
dbAgent = AssistantAgent(
    name="dbAgent",
    model_client=model_client,
    handoffs = ["orchestrator","user"], # can handoff to user if more info needed
    system_message="""You are a database assistant for a healthcare clinic application.
      Your task is to provide accurate and concise information about the user's insurance provider,
      medical history, and appointments based on the user's queries. If you do not have enough information
      to answer the user's question, do not continue to make assumptions;
        you must handoff the conversation to the user for more details""",
)
#example api agent to test handoff and swarm functionality
apiAgent = AssistantAgent(
    name="apiAgent",
    model_client=model_client,
    handoffs = ["orchestrator","user"],# can handoff to user if more info needed
    system_message="""You are a helpful assistant. Provide clear and concise answers.
      Your task is to provide information about clinic services, health tips, or general medical inquiries.
      If you do not have enough information to answer the user's question, do not continue to make assumptions;
     hand off the conversation to the user for more details.""",
)

termination = HandoffTermination(target="user") | TextMentionTermination("TERMINATE")
team = Swarm([dbAgent, apiAgent,orchestrator_agent], termination_condition=termination)


task = "I need to schedule an appointment."


async def run_team_stream() -> None:
    task_result = await Console(team.run_stream(task=task))
    last_message = task_result.messages[-1]

    while True:
        if isinstance(last_message, HandoffMessage) and last_message.target == "user":
            user_message = input("User: ")

            task_result = await Console(
                team.run_stream(
                    task= HandoffMessage(
                        source="user",
                        target=last_message.source,
                        content=user_message
                    )
                )
            )
            last_message = task_result.messages[-1]
        # Case 2: termination by agent
        elif isinstance(last_message, TextMentionTermination):
            print("Conversation terminated.")
            break

        # Case 3: normal end (no more messages)
        else:
            break


# Use asyncio.run(...) if you are running this in a script.
asyncio.run(run_team_stream())
