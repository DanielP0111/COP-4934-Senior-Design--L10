import unittest
from unittest.mock import patch
from adviceAgent import AdviceAgent
from autogen import UserProxyAgent, LLMConfig

# To run all tests from ai dir:        python -m unittest discover
# To run just these tests from ai dir: python -m unittest tests.testAdviceAgent

# Integration test for agent <-> tool communication.
class Test(unittest.TestCase):
    def setUp(self) -> None:
        self.user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            code_execution_config={"use_docker": False},
        )
        self.agent = AdviceAgent()
        self.agent.registerExecution(self.user_proxy)
        self.agent = self.agent.agent # Peak programming
        
        self.config = LLMConfig.from_json(path = "OAI_CONFIG_LIST.json")
    
    def runTest(self, message, params):
        with patch("tools.adviceApiTool.AdviceAPITool._run") as mock_run:
            mock_run.return_value = {
                "Title": "TestTitle",
                "Content": "TestContent"
            }

            self.user_proxy.initiate_chat(
                self.agent,
                message=message,
                llm_config=self.config,
            )
            
            mock_run.assert_called_once()
            
            args, kwargs = mock_run.call_args
            
            for key in params:
                if key in kwargs:
                    assert kwargs[key] == params[key]
    
    def testAllParams(self):
        message = "I would like to get some healthcare advice. I am a 35 year old female, who is pregnant, I am sexually active, and I do smoke tobacco."
        params = {
            "age": "35", 
            "pregnant": "yes", 
            "sex": "female", 
            "sexuallyActive": "yes", 
            "tobaccoUse": "yes"
        }
        
        self.runTest(message, params)

    def testSomeNo(self):
        message = "What are best practices for managing high blood pressure? I'm 20 years old, male, not pregnant, sexually active, and not a smoker."
        params = {
            "age": "20", 
            "pregnant": "no", 
            "sex": "male", 
            "sexuallyActive": "yes", 
            "tobaccoUse": "no"
        }
        
        self.runTest(message, params)

    def testSomeBlank(self):
        message = "I would like to get some healthcare advice. I am a 35 year old female, who is pregnant."
        
        # Keeping the blank params allows for the AI to either enter nothing or blank strings (both have the same result)
        params = {
            "age": "35", 
            "pregnant": "yes", 
            "sex": "female",
            "sexuallyActive": "",
            "tobaccoUse": ""
        }
        
        self.runTest(message, params)

if __name__ == "__main__":
    unittest.main()