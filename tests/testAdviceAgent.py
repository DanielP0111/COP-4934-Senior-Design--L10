import unittest
from unittest.mock import patch
from adviceAgent import AdviceAgent
from autogen import UserProxyAgent, LLMConfig

# To run all tests from main dir:      python -m unittest discover
# To run just this test from main dir: python -m unittest tests.testAdviceAgent

# They don't have pytest, so I'm using `unittest` for an integration test lol.
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
    
    def testAllParams(self):
        with patch("tools.adviceApiTool.AdviceAPITool._run") as mock_run:
            mock_run.return_value = {
                "Title": "TestTitle",
                "Content": "TestContent"
            }

            self.user_proxy.initiate_chat(
                self.agent,
                message="I would like to get some healthcare advice. I am a 35 year old female, who is pregnant, I am sexually active, and I do smoke tobacco.",
                llm_config=self.config,
            )

            mock_run.assert_called_once()

            args, kwargs = mock_run.call_args

            assert kwargs["age"] == "35"
            assert kwargs["pregnant"] == "yes"
            assert kwargs["sex"] == "female"
            assert kwargs["sexuallyActive"] == "yes"
            assert kwargs["tobaccoUse"] == "yes"

    def testSomeNo(self):
        with patch("tools.adviceApiTool.AdviceAPITool._run") as mock_run:
            mock_run.return_value = {
                "Title": "TestTitle",
                "Content": "TestContent"
            }

            self.user_proxy.initiate_chat(
                self.agent,
                message="What are best practices for managing high blood pressure? I'm 20 years old, male, not pregnant, sexually active, and not a smoker.",
                llm_config=self.config,
            )

            mock_run.assert_called_once()

            args, kwargs = mock_run.call_args

            assert kwargs["age"] == "20"
            assert kwargs["pregnant"] == "no"
            assert kwargs["sex"] == "male"
            assert kwargs["sexuallyActive"] == "yes"
            assert kwargs["tobaccoUse"] == "no"

    def testSomeBlank(self):
        with patch("tools.adviceApiTool.AdviceAPITool._run") as mock_run:
            mock_run.return_value = {
                "Title": "TestTitle",
                "Content": "TestContent"
            }

            self.user_proxy.initiate_chat(
                self.agent,
                message="I would like to get some healthcare advice. I am a 35 year old female, who is pregnant.",
                llm_config=self.config,
            )

            mock_run.assert_called_once()

            args, kwargs = mock_run.call_args

            assert kwargs["age"] == "35"
            assert kwargs["pregnant"] == "yes"
            assert kwargs["sex"] == "female"
            
            # Allow either just the three parameters, or blanks on the other two.
            expected_keys = {"age", "pregnant", "sex"}
            if(set(kwargs.keys()) == expected_keys):
                assert set(kwargs.keys()) == expected_keys
            
            else:
                assert kwargs["sexuallyActive"] == ""
                assert kwargs["tobaccoUse"] == ""

if __name__ == "__main__":
    unittest.main()