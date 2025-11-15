# agent specialziing in look up medication prices from CostPlusDrugs
# uses webParseTool to search for medications using DrugPriceLookupTool

from autogen import UserProxyAgent
from baseAgent import BaseAgent
from tools.webParseTool import DrugPriceLookupTool

# extends BaseAgent. provides drug prices using the DrugPriceLookupTool
# ex. of queries it can handle:
# "What is the price of metformin?"
# "How much does lisinopril 10mg cost?"
# "Compare prices for atorvastatin"

class PriceAgent(BaseAgent):
    def __init__(self):
        self.name = "PriceAgent"
        self.description = "A price agent which finds and summarizes drug price information."
        self.system_message = (
            "You are a medication price agent specialized in finding drug prices from Cost Plus Drugs."
            "You have access to a tool that searches their complete medication database."

            "When a user asks about medication prices:"
            "1. Use the DrugPriceLookupTool with the medication name"
            "2. If multiple results are returned, present the top 3-5 options clearly"
            "3. ALways include: medication name, strength, form, quantity, and price"
            "4. Mention that prices are from Cost Plus Drugs"
            "5. If the exact drug isn't found, suggest the closest matches"

            "IMPORTANT:"
            "Do NOT make up or guess prices - only use the data from the tool!"
            "If tool returns no results, inform the user the medication wasn't found"
            "Present prices clearly: both per-unit and total package price"
            "Include the URL so users can view more details"

            "After providing the price information, say 'TERMINATE' to end the conversation."

            "CONVERSATION PROTOCOL:"
            "1. Only speak when directly asked a question or when you have the specific information requested."
            "2. If another agent can handle the query, stay silent."
            "3. Default to silence unless you're certain your input is needed."
        )

        self.tools = [DrugPriceLookupTool()]
        super().__init__(
            name=self.name,
            description = self.description,
            system_message=self.system_message,
            tools=self.tools
        )
    

# testing

# returns list of test queries to use
def get_test_queries():
    return [
        "What is the price of metformin?",
        "How much does lisinopril 10mg cost?",
        "Price for albuterol inhaler",
        "What does atorvastatin cost at Cost Plus Drugs?",
        "How much is amlodipine?",
    ]

# testing block
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