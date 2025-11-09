from autogen import UserProxyAgent, LLMConfig
from baseAgent import BaseAgent
from tools.dbTool import (
    DatabaseConnection,
    QueryPatientInfoTool,
    QueryMedicalHistoryTool,
    QueryAppointmentsTool,
    QueryPrescriptionsTool
)

# activate .venv and run:
# pip install sqlalchemy langchain langchain-community ag2[ollama] ag2[openai]

# database agent using SQLAlchemy to query patient healthcare data
# any data about the user
# agent integrates with the baseAgent pattern for easy orchestrator integration
# easy to switch between local testing and a DB in a container in our server via .env file

class DBAgent(BaseAgent):
    # database agent that queries patient info
    # extends baseAgent, provides specialized tools for accessing patient data from a DB

    def __init__(self, db_connection: DatabaseConnection):
        self.name = "DBAgent"
        self.description = "A db agent which collects and informs about a user's basic information, medical history, appointments, and prescriptions."
        self.system_message = (
            "You are a database agent specialized in querying patient healthcare data. "

            "You have access to tools that can retrieve:\n"
            "1. Patient basic information (Name, date of birth, contact)\n"
            "2. Medical history (conditions, allergies, surgeries)\n"
            "3. Appointments\n"
            "4. Prescriptions (active or all medications)\n\n"

            "ALWAYS use the appropriate tool to answer queries. Do NOT make up or hallucinate information. "
            "If a user asks about their data, assume their user_id is 1001 unless specified otherwise. "
            "Return clear, concise responses based on the results of the query. "

            "After providing the answer, say 'TERMINATE' to end the conversation."
            
            "CONVERSATION PROTOCOL:"
            "1. Only speak when directly asked a question or when you have the specific information requested."
            "2. If another agent can handle the query, stay silent."
            "3. Default to silence unless you're certain your input is needed."
        )

        self.tools = [
            QueryPatientInfoTool(db_connection),
            QueryMedicalHistoryTool(db_connection),
            QueryAppointmentsTool(db_connection),
            QueryPrescriptionsTool(db_connection)
        ]

        super().__init__(
            name=self.name,
            description = self.description,
            system_message=self.system_message,
            tools=self.tools
        )

# testing / output section
def get_test_queries():
    # creates and returns a list of test queries to validate that the agent is working
    return [
        "What are my appointments?",
        "Do I have any medication allergies?",
        "What medications am I currently taking?",
        "What's my medical history?",
    ]

if __name__ == "__main__":
    print("="*50)
    print("initializing database agent...")
    print("="*50)

    # init db connection (in this case for testing it's in-memory)
    print("\n1. setting up database connection...")
    db_connection = DatabaseConnection()

    # test db connection
    print("\n2. testing database connection...")
    db_connection.test_connection()

    # make the user proxy
    print("\n3. creating user proxy...")
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=2,
        code_execution_config={"use_docker": False},
    )

    # init the db agent
    print("\n4. initializing DBAgent...")
    db_agent = DBAgent(db_connection)

    # register tools for execution
    print("\n5. registering tools for execution...")
    db_agent.registerExecution(user_proxy)

    print("\n" + "="*50)
    print("running test queries...")
    print("="*50)

    queries = get_test_queries()
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*50}")
        print(f"TEST QUERY {i}: {query}")
        print(f"\n{'='*50}")

        result = user_proxy.initiate_chat(
            db_agent.agent,
            message=query
        )

        print(f"\nFinal Result: {result.summary}\n")

    print("\n" + "="*50)
    print("all tests completed!")
    print("="*50)
