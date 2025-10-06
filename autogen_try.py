import autogen

# Load the configuration from the OAI_CONFIG_LIST file
config_list_ollama = autogen.config_list_from_json(
    env_or_file= "OAI_CONFIG_LIST.json"

)

# Create the agents
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config =config_list_ollama[0],
    system_message="You are a helpful assistant. Provide clear and concise answers.",
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply= 1,
    code_execution_config={"work_dir": "coding",
                           "use_docker": False},
)

# Start the conversation
user_proxy.initiate_chat(
    assistant,
    message="Tell me 3 facts about the University of Central Florida.",
)
