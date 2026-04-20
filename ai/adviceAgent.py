from baseAgent import BaseAgent
from tools.adviceApiTool import AdviceAPITool
from tools.webParseTool import HTMLParserTool

class AdviceAgent(BaseAgent):
    def __init__(self, prompts):
        self.name = "AdviceAgent"
        self.description = prompts["descriptions"]
        self.system_message = prompts["instructions"]
        self.tools = [AdviceAPITool(), HTMLParserTool()]
        
        super().__init__(
            name = self.name,
            description = self.description,
            system_message = self.system_message,
            tools = self.tools
        )
