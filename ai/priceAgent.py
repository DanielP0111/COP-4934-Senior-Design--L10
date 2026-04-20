# agent specialziing in look up medication prices from CostPlusDrugs
# uses webParseTool to search for medications using DrugPriceLookupTool

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
    