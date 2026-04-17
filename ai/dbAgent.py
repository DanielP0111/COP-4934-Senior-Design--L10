from autogen import UserProxyAgent
from baseAgent import BaseAgent
from tools.dbTool import (
    DatabaseConnection,
    QueryPatientInfoTool,
    QueryMedicalHistoryTool,
    QueryAppointmentsTool,
    QueryPrescriptionsTool
)

class DBAgent(BaseAgent):
    def __init__(self, db_connection: DatabaseConnection, prompts):
        self.name = "DBAgent"
        self.description = prompts["descriptions"]
        self.system_message = prompts["instructions"]

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

def get_test_queries():
    return [
        "What are my appointments? My user ID is 1001.",
        "Do I have any medication allergies? My user ID is 1001.",
        "What medications am I currently taking? My user ID is 1001.",
        "What's my medical history? My user ID is 1001.",
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
