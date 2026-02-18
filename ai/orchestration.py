from autogen import ConversableAgent, LLMConfig,  UserProxyAgent
from autogen.agentchat import initiate_group_chat
from autogen.agentchat.group import (
    AgentTarget,
    TerminateTarget,
    OnCondition,
    StringLLMCondition,
    ContextVariables
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
from utils import load_prompts
from messageCleanser import InputCleanser, OutputCleanser

LLM_CONFIG = LLMConfig.from_json(path = "OAI_CONFIG_LIST.json")
prompts = load_prompts()

def initAssistant(agent: BaseAgent, key, *args):
    assistant = agent(*args, prompts=prompts[key])
    assistant.agent.llm_config = LLM_CONFIG

    return assistant

def initOrchestrator(assistants: [BaseAgent]):

    orchestratorAgent = ConversableAgent(
        name = "orchestrator",
        system_message = prompts["orchestrator"]["instructions"],
        #max_consecutive_auto_reply=3,
        llm_config=LLM_CONFIG,
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

adviceAgent = initAssistant(AdviceAgent, "advice")
dbAgent = initAssistant(DBAgent, "db", DatabaseConnection())
diagnosisAgent = initAssistant(DiagnosisAgent, "diagnosis")
priceAgent = initAssistant(PriceAgent, "price")
statsAgent = initAssistant(StatAgent, "stats", CodeExecutor())

assistants = [adviceAgent, dbAgent, diagnosisAgent, priceAgent, statsAgent]

orchestratorAgent = initOrchestrator(assistants)

user = UserProxyAgent(
    name="user",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=2,
    code_execution_config={"use_docker": False},
)


def orchestrate(message, context_block):    
    agent_pattern = AutoPattern(
        agents=[orchestratorAgent] + [a.agent for a in assistants],
        initial_agent=orchestratorAgent,
        group_manager_args={"llm_config": LLM_CONFIG},
        user_agent=user,
        #context_variables=ContextVariables(data=context),
        summary_method="last_msg",
    )
    
    print("MESSAGE: ", message, "\nCONTEXT: ", context_block)
    
    input_cleanser = InputCleanser()
    clean_message = input_cleanser.cleanInput(message)
    
    full_message_with_context = context_block + clean_message

    if clean_message == "Greyhawk 10":
        return "I'm sorry. I'm afraid I can't do that."

    result, final_context, last_agent = initiate_group_chat(
        pattern=agent_pattern,
        messages=full_message_with_context,
        max_rounds=10,        
    )
    
    print(result.summary)
    
    print("RESULT: ", result, "\nFINAL CONTEXT: ", final_context, "\nLAST AGENT:", last_agent)
    
    reply = ""
        
    for response in result.chat_history:
        if response["role"] == "user" and response["name"] != "user":
            reply = response["content"]
            break
        if reply == "":
            reply = response["content"]
    
    output_cleanser = OutputCleanser()
    clean_reply = output_cleanser.cleanOutput(reply)
    
    print(clean_reply)
    
    return clean_reply

if __name__ == "__main__":
    message = "I am a 55 year old pregnant woman who smokes, can you give me some healthcare advice?"
    chat_context = {
        "user_name" : user,
        "query_history" : [message],
        "response_history" : [],
        "system_instructions" : [
            "You must respond to all messages in ENGLISH"
        ],
    }
    orchestrate(message, chat_context)
