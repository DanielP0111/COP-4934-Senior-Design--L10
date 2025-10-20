from autogen import ConversableAgent, LLMConfig,  UserProxyAgent
from autogen.agentchat import initiate_group_chat
from autogen.agentchat.group import (
    AgentNameTarget,
    AgentTarget,
    AskUserTarget,
    ContextExpression,
    ContextStr,
    ContextStrLLMCondition,
    ContextVariables,
    ExpressionAvailableCondition,
    ExpressionContextCondition,
    GroupChatConfig,
    GroupChatTarget,
    Handoffs,
    NestedChatTarget,
    OnCondition,
    OnContextCondition,
    ReplyResult,
    RevertToUserTarget,
    SpeakerSelectionResult,
    StayTarget,
    StringAvailableCondition,
    StringContextCondition,
    StringLLMCondition,
    TerminateTarget,
)

from autogen.agentchat.group.patterns import(
    DefaultPattern,
    ManualPattern,
    AutoPattern,
    RandomPattern,
    RoundRobinPattern,

)
from apiAgent import APIAgent
from dbAgent import DBAgent, DatabaseConnection

config = LLMConfig.from_json(path = "OAI_CONFIG_LIST.json")
llm_config = config

orchestratorMessage = """You are an orchestrator agent for a healthcare clinic application.
      Your task is to manage and coordinate the interactions between 
      the user and the other assistant agents. Do not answer the users questions yourself, you must always hand off to 
       another agent. Any questions the user has about their insurance provider,
      medical history, or appointments should be directed to the dbAgent. Any questions about clinic services,
      health tips, or general medical inquiries should be directed to the apiAgent.
      """

orchestratorAgent = ConversableAgent(
    name = "orchestrator",
    system_message = orchestratorMessage,
    max_consecutive_auto_reply= 2,
    llm_config= llm_config,
    human_input_mode= "TERMINATE"
)

apiAgent = APIAgent()
apiAgent.agent.llm_config = llm_config
dbAgent = DBAgent(DatabaseConnection)
dbAgent.agent.llm_config = llm_config

apiHandoffPrompt = """The user is asking for general healthcare advice, trying to determine the cause of a health
related issue, or asking for the cost of a medication."""

dbHandoffPrompt = """The user is asking about their medical history, past appointments, healthcare provider,
 or current prescriptions"""


orchestratorAgent.handoffs.add_llm_conditions([
        OnCondition(
            target=AgentTarget(apiAgent),
            condition=StringLLMCondition(prompt= apiHandoffPrompt),
        ),
        OnCondition(
            target=AgentTarget(dbAgent),
            condition=StringLLMCondition(prompt= dbHandoffPrompt),
        )
    ]
)


user = ConversableAgent(name="user", human_input_mode="ALWAYS")

# Create the pattern
agent_pattern = AutoPattern(
  agents=[orchestratorAgent, apiAgent.agent, dbAgent.agent],
  initial_agent= orchestratorAgent,
  group_manager_args={"llm_config": llm_config},
  user_agent=user
)

result, final_context, last_agent = initiate_group_chat(
    pattern=agent_pattern,
    messages="I have a headache and a fever what should i do?",
    max_rounds=10,
)





