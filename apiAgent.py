import autogen

# Continue following: https://www.youtube.com/watch?v=ffG0zaYtOF4 around 2:14
# class APIToolInput(BaseModel):
        

class APIAgent:
    def __init__(self, config):
        self.agent = autogen.AssistantAgent(
            name="API Agent",
            llm_config = config[0],
            system_message="""You are a healthcare professional. When prompted you will provide information about healthcare insurance
            providers and the cost of the medicine under a specific provider.""",
        )

if name == "__main__":
    config_list_ollama = autogen.config_list_from_json(
            env_or_file= "OAI_CONFIG_LIST.json"
    )
    
    apiAgent = APIAgent(config=config_list_ollama)
    
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply= 1,
        code_execution_config={"work_dir": "coding",
                            "use_docker": False},
    )

    user_proxy.initiate_chat(
        apiAgent,
        message="I have United Healthcare, how much will my month worth of Insulin cost?",
    )
