from autogen import UserProxyAgent
from baseAgent import BaseAgent
from tools.webParseTool import DrugPriceLookupTool

class PriceAgent(BaseAgent):
    def __init__(self, prompts):
        self.name = "PriceAgent"
        self.description = prompts["descriptions"]
        self.system_message = prompts["instructions"]
        self.tools = [DrugPriceLookupTool()]
        super().__init__(
            name=self.name,
            description = self.description,
            system_message=self.system_message,
            tools=self.tools
        )

def get_test_queries():
    return [
        "What is the price of metformin?",
        "How much does lisinopril 10mg cost?",
        "Price for albuterol inhaler",
        "What does atorvastatin cost at Cost Plus Drugs?",
        "How much is amlodipine?",
    ]

if __name__ == "__main__":
    print("initializing priceAgent...")

    print("\n1. creating user proxy...")
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=3,
        code_execution_config={"use_docker": False},
    )

    print("\n2. initializing priceAgent...")
    price_agent = PriceAgent()

    print("\n3. registering tools for execution...")
    price_agent.registerExecution(user_proxy)

    print("\n4. running test queries...")
    queries = get_test_queries()
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*50}")
        print(f"TEST QUERY {i}: {query}")
        print(f"\n{'='*50}")

        result = user_proxy.initiate_chat(
            price_agent.agent,
            message=query
        )

        print(f"\nfinal result: {result.summary}\n")
    

    print("testing completed.")