from autogen import ConversableAgent, LLMConfig,  UserProxyAgent
from autogen.agentchat import initiate_group_chat
from autogen.agentchat.group import (
    AgentTarget,
    OnCondition,
    StringLLMCondition,
)
from autogen.agentchat.group.patterns import(
    AutoPattern,
)
from baseAgent import BaseAgent
from adviceAgent import AdviceAgent
from dbAgent import DBAgent, DatabaseConnection

LLM_CONFIG = LLMConfig.from_json(path = "OAI_CONFIG_LIST.json")

def initAssistant(agent: BaseAgent, *args):
    assistant = agent(*args)
    assistant.agent.llm_config = LLM_CONFIG
    
    return assistant

def initOrchestrator(assistants: [BaseAgent]):
    orchestratorMessage = """You are an orchestrator agent for a healthcare clinic application.
      Your task is to manage and coordinate the interactions between 
      the user and the other assistant agents. Do not answer the users questions yourself, you must always hand off to 
       another agent. Any questions the user has about their insurance provider,
      medical history, or appointments should be directed to the dbAgent. Any questions about clinic services,
      health tips, or general medical inquiries should be directed to the adviceAgent.
      """

    orchestratorAgent = ConversableAgent(
        name = "orchestrator",
        system_message = orchestratorMessage,
        max_consecutive_auto_reply=2,
        llm_config=LLM_CONFIG,
        human_input_mode="TERMINATE"
    )
    
    for assistant in assistants:
        assistant.registerExecution(orchestratorAgent)
        
    return orchestratorAgent

# Can't think of a better way right now.
adviceAgent = initAssistant(AdviceAgent)
dbAgent = initAssistant(DBAgent, DatabaseConnection())

assistants = [adviceAgent, dbAgent]

orchestratorAgent = initOrchestrator(assistants)

adviceHandoffPrompt = """The user is asking for general healthcare advice, trying to determine the cause of a health
related issue, or asking for the cost of a medication."""

dbHandoffPrompt = """The user is asking about their medical history, past appointments, healthcare provider,
 or current prescriptions"""

# NOTE: This can be modularized further BUT we must add handoffPrompt to BaseAgent and hence every agent.
orchestratorAgent.handoffs.add_llm_conditions([
        OnCondition(
            target=AgentTarget(adviceAgent),
            condition=StringLLMCondition(prompt=adviceHandoffPrompt),
        ),
        OnCondition(
            target=AgentTarget(dbAgent),
            condition=StringLLMCondition(prompt=dbHandoffPrompt),
        )
    ]
)

user = ConversableAgent(name="user", human_input_mode="ALWAYS")

# Create the pattern
agent_pattern = AutoPattern(
  agents=[orchestratorAgent] + [a.agent for a in assistants],
  initial_agent=orchestratorAgent,
  group_manager_args={"llm_config": LLM_CONFIG},
  user_agent=user
)

result, final_context, last_agent = initiate_group_chat(
    pattern=agent_pattern,
    messages="I am a 55 year old pregnant woman who smokes, can you give me some healthcare advice?",
    max_rounds=10,
)
