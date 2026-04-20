from autogen import UserProxyAgent, LLMConfig
from baseAgent import BaseAgent
from tools.dbTool import (
    DatabaseConnection,
    Patient,
    MedicalHistory,
    Appointment,
    Prescription,
    QueryPatientInfoTool,
    QueryMedicalHistoryTool,
    QueryAppointmentsTool,
    QueryPrescriptionsTool,
    UpdatePatientRecordTool,
    AddPatientRecordTool,
    DeletePatientRecordTool
)

class DBAgent(BaseAgent):
    # database agent that queries patient info
    # extends baseAgent, provides specialized tools for accessing patient data from a DB

    def __init__(self, db_connection: DatabaseConnection, prompts):
        self.name = "DBAgent"
        self.description = prompts["descriptions"]
        self.system_message = prompts["instructions"]

        models = {
            "patients": Patient,
            "medical_history": MedicalHistory,
            "appointments": Appointment,
            "prescriptions": Prescription
        }

        self.tools = [
            QueryPatientInfoTool(db_connection),
            QueryMedicalHistoryTool(db_connection),
            QueryAppointmentsTool(db_connection),
            QueryPrescriptionsTool(db_connection),
            UpdatePatientRecordTool(db_connection, models),
            AddPatientRecordTool(db_connection, models),
            DeletePatientRecordTool(db_connection, models)
        ]

        super().__init__(
            name=self.name,
            description = self.description,
            system_message=self.system_message,
            tools=self.tools
        )
