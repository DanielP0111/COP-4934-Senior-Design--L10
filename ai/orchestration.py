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
from diagnosisAgent import DiagnosisAgent
from priceAgent import PriceAgent
from statsAgent import StatAgent, CodeExecutor

LLM_CONFIG = LLMConfig.from_json(path = "OAI_CONFIG_LIST.json")

def initAssistant(agent: BaseAgent, *args):
    assistant = agent(*args)
    assistant.agent.llm_config = LLM_CONFIG

    return assistant

def initOrchestrator(assistants: [BaseAgent]):
    orchestratorMessage = """You are an orchestrator agent for a healthcare clinic application.
      Your task is to manage and coordinate the interactions between 
      the user and the other assistant agents. Do not answer the users questions yourself, you must always hand off to 
      another agent. Do not delegate unless it was the user's query. If the is nothing to delegate, terminate the conver
      If you delegate back to yourself, terminate the conversation.
      Any questions the user has about their insurance provider,
      medical history, or appointments should be directed to the dbAgent. Any questions about clinic services,
      health tips, or general medical inquiries should be directed to the adviceAgent.
      """

    orchestratorAgent = ConversableAgent(
        name = "orchestrator",
        system_message = orchestratorMessage,
        #original is 0
        #max_consecutive_auto_reply=3,
        llm_config=LLM_CONFIG,
        #changed
        human_input_mode="NEVER"
    )
    
    conditions = []
    
    for assistant in assistants:
        assistant.registerExecution(orchestratorAgent)
        
        conditions.append(
            OnCondition(
                target=AgentTarget(assistant),
                condition=StringLLMCondition(prompt=assistant.description),
            )
        )
    
    orchestratorAgent.handoffs.add_llm_conditions(conditions)
    
    return orchestratorAgent

# NOTE: Can't think of a better way right now, so new agents need this initialization.
adviceAgent = initAssistant(AdviceAgent)
dbAgent = initAssistant(DBAgent, DatabaseConnection())
diagnosisAgent = initAssistant(DiagnosisAgent)
priceAgent = initAssistant(PriceAgent)
statsAgent = initAssistant(StatAgent, CodeExecutor())

assistants = [adviceAgent, dbAgent, diagnosisAgent, priceAgent, statsAgent]

orchestratorAgent = initOrchestrator(assistants)

user = UserProxyAgent(
    name="user",
    human_input_mode="TERMINATE",
    #original 2
    max_consecutive_auto_reply=2,
    code_execution_config={"use_docker": False},
)

agent_pattern = AutoPattern(
    agents=[orchestratorAgent] + [a.agent for a in assistants],
    initial_agent=orchestratorAgent,
    group_manager_args={"llm_config": LLM_CONFIG},
    user_agent=user
)

def orchestrate(message: str):
    result, final_context, last_agent = initiate_group_chat(
        pattern=agent_pattern,
        messages=message,
        max_rounds=10,
    )
    return result

# Doing it this way since Infra team wants this as a function.
if __name__ == "__main__":
    orchestrate()
