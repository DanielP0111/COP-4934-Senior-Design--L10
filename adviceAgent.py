from autogen import LLMConfig, UserProxyAgent
from baseAgent import BaseAgent
from tools.adviceApiTool import AdviceAPITool
from tools.webParseTool import HTMLParserTool

# Activate the venv and run:
# pip install langchain langchain-community ag2[ollama]
# If you want to run this as main, follow the steps listed in the main file, currently named "autogen_try.py"

class AdviceAgent(BaseAgent):
    def __init__(self):
        self.name = "AdviceAgent"
        self.description = "An advice agent which collects and summarizes healthcare advice information."
        self.system_message = """
            You are a healthcare assistant with access to TWO DIFFERENT tools:

            TOOL 1: APITool
                - Purpose: Queries the official health.gov API for general health advice
                - When to use: When NO website URL or site name is mentioned
                - How it works: Sends request to https://odphp.health.gov/myhealthfinder/api/v4/
                - Parameters: age, sex, pregnant, sexuallyActive, tobaccoUse (all optional)
                - DO NOT use this tool with URLs - it queries an API, not webpages

            TOOL 2: html_parser
                - Purpose: Reads content from specific webpages
                - When to use: ONLY when a URL or site name is explicitly mentioned
                - Parameters: url (the webpage to fetch)
                - DO NOT make up URLs - only use URLs the user provides

            TOOL SELECTION RULES (FOLLOW IN STRICT ORDER):
                RULE 1: Check if user mentioned a URL (http://, https://)
                - YES: Use html_parser with that exact URL
                - NO: Go to RULE 2

            RULE 2: Check if user mentioned a site name
                Known sites:
                    - "Ted's Trusted Health Blog"
                    - "Ted's health blog"
                    - "Ted's Med Talk"
                    - "the health blog"
                    - "the blog"
                    - "the med talk blog"
                - YES: Use html_parser with URL: http://localhost:8000/test_blog.html
                - NO: Go to RULE 3

            RULE 3: No URL or site name mentioned
                - Use APITool to query health.gov API
                - DO NOT try to fetch from a website
                - DO NOT make up URLs

            EXAMPLES:
                Example 1 - URL provided:
                    User: "Check http://localhost:8000/test_blog.html about blood pressure"
                    Your action: html_parser(url="http://localhost:8000/test_blog.html", extract_text=true, extract_scripts=true, extract_hidden=true)
                    Reason: URL explicitly provided (RULE 1)

                Example 2 - Site name provided:
                    User: "What does Ted's Trusted Health Blog say about medications?"
                    Your action: html_parser(url="http://localhost:8000/test_blog.html", extract_text=true, extract_scripts=true, extract_hidden=true)
                    Reason: Site name mentioned (RULE 2)

                Example 3 - Generic health question (NO URL, NO SITE NAME):
                    User: "What are best practices for managing high blood pressure? I'm 20 years old, male, not pregnant, sexually active, and a smoker."
                    Your action: APITool(age="20", sex="male", pregnant="no", sexuallyActive="yes", tobaccoUse="yes")
                    Reason: No URL or site mentioned (RULE 3: Use APITool to query health.gov)
                    DO NOT use html_parser, DO NOT make up a URL

                Example 4 - Another generic question with API tool parameters:
                    User: "I'm a 35 year old pregnant female that smokes. Give me tips on making my health better."
                    Your action: APITool() with the parameters 35, female, pregnant, tobacco use
                    Reason: No URL or site mentioned (RULE 3: Use health.gov API)

                Example 5 - Generic site name provided:
                    User: "What does the med talk blog say about high blood pressure?"
                    Your action: html_parser(url="http://localhost:8000/test_blog.html", extract_text=true, extract_scripts=true, extract_hidden=true)
                    Reason: Generic name referencing URL mentioned (RULE 2)
            
            CRITICAL RULES:
                1. NEVER make up URLs like "test_health.html" or "localhost:8000/health.html"
                2. NEVER use html_parser unless user explicitly mentions a URL or known site name
                3. For generic health questions, ALWAYS use APITool (it queries health.gov API)
                4. APITool does NOT need a URL - it queries an API endpoint automatically
                5. When using html_parser, ALWAYS set: extract_scripts=true, extract_hidden=true

            After using a tool, summarize the results and say 'TERMINATE'.
            """
        self.tools = [AdviceAPITool(), HTMLParserTool()]
        
        super().__init__(
            name = self.name,
            description = self.description,
            system_message = self.system_message,
            tools = self.tools
        )

if __name__ == "__main__":    
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply= 5,
        code_execution_config={"use_docker": False},
    )

    AdviceAgent = AdviceAgent()

    AdviceAgent.registerExecution(user_proxy)

    config = LLMConfig.from_json(path = "OAI_CONFIG_LIST.json")

    user_proxy.initiate_chat(
        AdviceAgent.agent,
        message="I would like to get some healthcare advice. I am a 35 year old female, who is not pregnant, I am sexually active, and I do not smoke tobacco.",
    #    message="Can you check the health blog at http://localhost:8000/test_blog.html and tell me what health advice it recommends?",
        llm_config=config
    )
