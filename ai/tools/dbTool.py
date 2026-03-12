from typing import Dict, Any, Type, Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, Date, JSON, ForeignKey, Time
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime
import os

# pip install sqlalchemy should have alr been ran

Base = declarative_base()

# below includes local database setup for testing with a real SQL database
# this in-memory DB will not be used for testing in prod
# instead, the connection string will be changed to our DB in a container located on Bill

# models for SQLAlchemy that define schema
class Patient(Base):
    __tablename__ = 'patients'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(Text, nullable=False)
    dob = Column(Date)
    gender = Column(Text)
    email = Column(Text)
    phone = Column(Text)
    
    medical_history = relationship("MedicalHistory", back_populates="patient", uselist=False, cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
    prescriptions = relationship("Prescription", back_populates="patient", cascade="all, delete-orphan")


class MedicalHistory(Base):
    __tablename__ = 'medical_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('patients.user_id'), nullable=False)
    conditions = Column(Text)
    allergies = Column(Text)
    surgeries = Column(Text)
    
    patient = relationship("Patient", back_populates="medical_history")


class Appointment(Base):
    __tablename__ = 'appointments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('patients.user_id', ondelete='CASCADE'), nullable=False, index=True)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    doctor = Column(Text)
    specialty = Column(Text)
    type = Column(Text)
    status = Column(Text)
    
    patient = relationship("Patient", back_populates="appointments")


class Prescription(Base):
    __tablename__ = 'prescriptions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('patients.user_id', ondelete='CASCADE'), nullable=False, index=True)
    medication = Column(Text)
    dosage = Column(Text)
    frequency = Column(Text)
    prescribing_doctor = Column(Text)
    start_date = Column(Date)
    refills_remaining = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    
    patient = relationship("Patient", back_populates="prescriptions")

# connection manager for database
class DatabaseConnection:
    # manages SQLAlchemy db connection/session

    def __init__(self, connection_string: Optional[str] = None):
        # if no connection string provided, default to in-memory db
        if connection_string is None:
            connection_string = os.getenv("DATABASE_URL", "sqlite:///:memory:")
        
        self.connection_string = connection_string
        self.engine = create_engine(connection_string, echo=False)
        self.Session = sessionmaker(bind=self.engine)

        # for testing;
        # only make tables/seed data for sqlite
        if "sqlite" in connection_string.lower():
            self._create_tables()
            self._seed_data()
        
    def _create_tables(self):
        # creates all db tables
        Base.metadata.create_all(self.engine)
        print("[DB] Tables created successfully")

    def _seed_data(self):
        # seeds db with mock test data
        session = self.Session()
        
        try:
            # check if data already exists
            if session.query(Patient).count() > 0:
                print("[DB] Data already seeded")
                return
            
            # 1001: Sarah Johnson
            patient1 = Patient(
                user_id=1001,
                name="Sarah Johnson",
                dob="1985-03-15",
                email="sarah.j@email.com",
                phone="555-0101"
            )
            
            history1 = MedicalHistory(
                user_id=1001,
                conditions=["Type 2 Diabetes", "Hypertension"],
                allergies=["Penicillin", "Sulfa drugs"],
                surgeries=["Appendectomy (2010)"]
            )
            
            appointments1 = [
                Appointment(
                    id="A101", user_id=1001, date="2025-10-20", time="10:00 AM",
                    doctor="Dr. Emily Smith", specialty="Endocrinology",
                    type="Follow-up", status="scheduled"
                ),
                Appointment(
                    id="A102", user_id=1001, date="2025-11-15", time="2:30 PM",
                    doctor="Dr. Robert Kim", specialty="Cardiology",
                    type="Routine Checkup", status="scheduled"
                ),
                Appointment(
                    id="A103", user_id=1001, date="2025-09-15", time="9:00 AM",
                    doctor="Dr. Emily Smith", specialty="Endocrinology",
                    type="Consultation", status="completed"
                )
            ]
            
            prescriptions1 = [
                Prescription(
                    id="RX101", user_id=1001, medication="Metformin", dosage="500mg",
                    frequency="Twice daily", prescribing_doctor="Dr. Emily Smith",
                    start_date="2024-01-15", refills_remaining=3, active=True
                ),
                Prescription(
                    id="RX102", user_id=1001, medication="Lisinopril", dosage="10mg",
                    frequency="Once daily", prescribing_doctor="Dr. Robert Kim",
                    start_date="2024-03-20", refills_remaining=5, active=True
                )
            ]
            
            # 1002: Michael Chen
            patient2 = Patient(
                user_id=1002,
                name="Michael Chen",
                dob="1992-07-22",
                email="mchen@email.com",
                phone="555-0102"
            )
            
            history2 = MedicalHistory(
                user_id=1002,
                conditions=[],
                allergies=[],
                surgeries=[]
            )
            
            appointments2 = [
                Appointment(
                    id="A201", user_id=1002, date="2025-12-01", time="11:00 AM",
                    doctor="Dr. Sarah Lee", specialty="General Practice",
                    type="Annual Physical", status="scheduled"
                )
            ]
            
            # 1003: Eleanor Martinez
            patient3 = Patient(
                user_id=1003,
                name="Eleanor Martinez",
                dob="1958-11-08",
                email="eleanor.m@email.com",
                phone="555-0103"
            )
            
            history3 = MedicalHistory(
                user_id=1003,
                conditions=["Osteoarthritis", "Hypertension", "Atrial Fibrillation"],
                allergies=["Codeine"],
                surgeries=["Hip Replacement (2020)", "Cataract Surgery (2022)"]
            )
            
            appointments3 = [
                Appointment(
                    id="A301", user_id=1003, date="2025-10-18", time="3:00 PM",
                    doctor="Dr. Michael Brown", specialty="Orthopedics",
                    type="Follow-up", status="scheduled"
                ),
                Appointment(
                    id="A302", user_id=1003, date="2025-10-25", time="10:30 AM",
                    doctor="Dr. Jennifer Park", specialty="Cardiology",
                    type="Routine Checkup", status="scheduled"
                ),
                Appointment(
                    id="A303", user_id=1003, date="2025-09-20", time="2:00 PM",
                    doctor="Dr. Michael Brown", specialty="Orthopedics",
                    type="Post-op Checkup", status="completed"
                )
            ]
            
            prescriptions3 = [
                Prescription(
                    id="RX301", user_id=1003, medication="Eliquis", dosage="5mg",
                    frequency="Twice daily", prescribing_doctor="Dr. Jennifer Park",
                    start_date="2023-06-10", refills_remaining=2, active=True
                ),
                Prescription(
                    id="RX302", user_id=1003, medication="Amlodipine", dosage="5mg",
                    frequency="Once daily", prescribing_doctor="Dr. Jennifer Park",
                    start_date="2023-06-10", refills_remaining=4, active=True
                ),
                Prescription(
                    id="RX303", user_id=1003, medication="Acetaminophen", dosage="500mg",
                    frequency="As needed", prescribing_doctor="Dr. Michael Brown",
                    start_date="2024-08-15", refills_remaining=0, active=False
                )
            ]
            
            # 1004: James Wilson
            patient4 = Patient(
                user_id=1004,
                name="James Wilson",
                dob="1978-05-30",
                email="jwilson@email.com",
                phone="555-0104"
            )
            
            history4 = MedicalHistory(
                user_id=1004,
                conditions=["Asthma"],
                allergies=["Shellfish", "Latex"],
                surgeries=["ACL Repair (2015)"]
            )
            
            appointments4 = [
                Appointment(
                    id="A401", user_id=1004, date="2025-11-10", time="4:00 PM",
                    doctor="Dr. Amanda White", specialty="Pulmonology",
                    type="Asthma Management", status="scheduled"
                )
            ]
            
            prescriptions4 = [
                Prescription(
                    id="RX401", user_id=1004, medication="Albuterol Inhaler", dosage="90mcg",
                    frequency="As needed", prescribing_doctor="Dr. Amanda White",
                    start_date="2024-05-01", refills_remaining=2, active=True
                )
            ]
            
            # add all of them to the session
            session.add_all([patient1, patient2, patient3, patient4])
            session.add_all([history1, history2, history3, history4])
            session.add_all(appointments1 + appointments2 + appointments3 + appointments4)
            session.add_all(prescriptions1 + prescriptions3 + prescriptions4)
            
            session.commit()
            print("[DB] Mock data seeded successfully")
            
        except Exception as e:
            session.rollback()
            print(f"[DB] Error seeding data: {e}")
        finally:
            session.close()

    def get_session(self):
        return self.Session()

    def test_connection(self):
        try:
            session = self.get_session()
            # test query
            count = session.query(Patient).count()
            session.close()
            print(f"DB connection successful. Found {count} patients.")
            return True
        except Exception as e:
            print(f"!!! DB connection failed: {e}")
            return False
        

# database tool classes

# query patient info
class QueryPatientInfoArgs(BaseModel):
    user_id: int = Field(..., description="Patient user ID")

class QueryPatientInfoTool(BaseTool):
    name: str = "query_patient_info"
    description: str = "Query basic patient information including name, DOB, and contact details."
    args_schema: Type[BaseModel] = QueryPatientInfoArgs
    db_connection: Any = None

    def __init__(self, db_connection: DatabaseConnection):
        super().__init__()
        self.db_connection = db_connection
    
    def _run(self, user_id: int) -> Dict[str, Any]:
        print(f"[DB tool] querying patient info for user_id={user_id}")
        session = self.db_connection.get_session()

        try:
            patient = session.query(Patient).filter_by(user_id=user_id).first()
            if not patient:
                return {"error": f"patient with user_id {user_id} not found"}
            
            return {
                "name": patient.name,
                "dob": patient.dob,
                "email": patient.email,
                "phone": patient.phone
            }
        except Exception as e:
            return{"error": f"DB error: {str(e)}"}
        finally:
            session.close()
    
    async def _arun(self, user_id: int) -> Dict[str, Any]:
        return self._run(user_id)
    
# query medical history
class QueryMedicalHistoryArgs(BaseModel):
    user_id: int = Field(..., description="Patient user ID")

class QueryMedicalHistoryTool(BaseTool):
    name: str = "query_medical_history"
    description: str = "Query patient medical history including conditions, allergies, and past surgeries."
    args_schema: Type[BaseModel] = QueryMedicalHistoryArgs
    db_connection: Any = None

    def __init__(self, db_connection: DatabaseConnection):
        super().__init__()
        self.db_connection = db_connection
    
    def _run(self, user_id: int) -> Dict[str, Any]:
        print(f"[DB tool] querying medical history for user_id={user_id}")
        session = self.db_connection.get_session()

        try:
            history = session.query(MedicalHistory).filter_by(user_id=user_id).first()
            if not history:
                return {"error": f"medical history for user_id {user_id} not found"}
            
            return {
                "conditions": history.conditions or "",
                "allergies": history.allergies or "",
                "surgeries": history.surgeries or ""
            }
        except Exception as e:
            return {"error": f"DB error: {str(e)}"}
        finally:
            session.close()

    async def _arun(self, user_id: int) -> Dict[str, Any]:
        return self._run(user_id)

# query appointments
class QueryAppointmentsArgs(BaseModel):
    user_id: int = Field(..., description="patient user ID")

class QueryAppointmentsTool(BaseTool):
    name: str = "query_appointments"
    description: str = "Query patient appointments."
    args_schema: Type[BaseModel] = QueryAppointmentsArgs
    db_connection: Any = None
    
    def __init__(self, db_connection: DatabaseConnection):
        super().__init__()
        self.db_connection = db_connection
    
    def _run(self, user_id: int) -> Dict[str, Any]:
        print(f"[DB tool] querying appointments for user_id={user_id}")
        session = self.db_connection.get_session()
        
        try:
            appointments = session.query(Appointment).filter_by(user_id=user_id).all()
            
            if not appointments:
                return {"error": f"no appointments found for user_id {user_id}"}
            
            appointments_list = []
            for apt in appointments:
                appointments_list.append({
                    "id": apt.id,
                    "date": apt.date,
                    "time": apt.time,
                    "doctor": apt.doctor,
                    "specialty": apt.specialty,
                    "type": apt.type,
                    "status": apt.status
                })
            
            return {
                "appointments": appointments_list,
                "count": len(appointments_list)
            }
        except Exception as e:
            return {"error": f"DB error: {str(e)}"}
        finally:
            session.close()
    
    async def _arun(self, user_id: int) -> Dict[str, Any]:
        return self._run(user_id)


# Tool 4: Query Prescriptions
class QueryPrescriptionsArgs(BaseModel):
    user_id: int = Field(..., description="patient user ID")
    active_only: bool = Field(True, description="if True, return only active prescriptions")

class QueryPrescriptionsTool(BaseTool):
    name: str = "query_prescriptions"
    description: str = "Query patient prescriptions. By default returns only active prescriptions."
    args_schema: Type[BaseModel] = QueryPrescriptionsArgs
    db_connection: Any = None
    
    def __init__(self, db_connection: DatabaseConnection):
        super().__init__()
        self.db_connection = db_connection
    
    def _run(self, user_id: int, active_only: bool = True) -> Dict[str, Any]:
        print(f"[DB tool] querying prescriptions for user_id={user_id}, active_only={active_only}")
        session = self.db_connection.get_session()
        
        try:
            query = session.query(Prescription).filter_by(user_id=user_id)
            
            if active_only:
                query = query.filter_by(active=True)
            
            prescriptions = query.all()
            
            if not prescriptions:
                return {"error": f"no prescriptions found for user_id {user_id}"}
            
            prescriptions_list = []
            for rx in prescriptions:
                prescriptions_list.append({
                    "id": rx.id,
                    "medication": rx.medication,
                    "dosage": rx.dosage,
                    "frequency": rx.frequency,
                    "prescribing_doctor": rx.prescribing_doctor,
                    "start_date": rx.start_date,
                    "refills_remaining": rx.refills_remaining,
                    "active": rx.active
                })
            
            return {
                "prescriptions": prescriptions_list,
                "count": len(prescriptions_list)
            }
        except Exception as e:
            return {"error": f"DB error: {str(e)}"}
        finally:
            session.close()
    
    async def _arun(self, user_id: int, active_only: bool = True) -> Dict[str, Any]:
        return self._run(user_id, active_only)

# - database write tools -
# tool 1: update patient records
class UpdatePatientRecordArgs(BaseModel):
    user_id: int = Field(..., description="Patient user ID")
    table: str = Field(..., description="Table to update")
    record_id: Optional[int] = Field(None, description="Record ID for appointments/prescriptions")
    updates: Dict[str, Any] = Field(..., description="Dict of field names and new values to update")

class UpdatePatientRecordTool(BaseTool):
    name: str = "update_patient_record"
    description: str = """Updates patient records inside the database.
    Has capability to modify records in the patients, appointments, and medical history tables.
    Requires user_id to identify the patient & a record_id if appointments are being modified
    Pass updates as a dictionary of field names and their new values. """
    args_schema: Type[BaseModel] = UpdatePatientRecordArgs
    db_connection: Any = None
    TABLE_MAP: Dict[str, Any] = {}

    IMMUTABLE_FIELDS: Dict[str, set] = {
        "_all": {"user_id"},  # Immutable across all tables
        "patients": {"dob"},  # Immutable for patients specifically
    }

    def __init__(self, db_connection: DatabaseConnection, models: Dict[str, Any] = None):
        super().__init__()
        self.db_connection = db_connection
        self.TABLE_MAP = models or {
            "patients": Patient,
            "medical_history": MedicalHistory,
            "appointments": Appointment,
        }
    
    def _run(self, user_id: int, table: str, updates: Dict[str, Any], record_id: Optional[int] = None) -> Dict[str, Any]:
        print(f"[DB write] updating {table} for user_id={user_id}, record_id={record_id}, updates={updates}")

        if table not in self.TABLE_MAP:
            return {"error": f"Invalid table: {table}. Valid tables: {list(self.TABLE_MAP.keys())}"}
        
        # Filter out immutable fields before touching the DB
        immutable = self.IMMUTABLE_FIELDS["_all"] | self.IMMUTABLE_FIELDS.get(table, set())
        blocked_fields = immutable & updates.keys()
        if blocked_fields:
            print(f"[DB write] warning: attempt to modify immutable fields {blocked_fields} on {table} — skipping")
            updates = {k: v for k, v in updates.items() if k not in immutable}

        if not updates:
            return {"error": f"No updatable fields provided. Fields {blocked_fields} are immutable for {table}."}

        model = self.TABLE_MAP[table]
        session = self.db_connection.get_session()

        try:
            if table in ["appointments"]:
                if record_id is None:
                    return {"error": f"record_id is required for {table} table"}
                record = session.query(model).filter_by(user_id=user_id, id=record_id).first()
            else:
                record = session.query(model).filter_by(user_id=user_id).first()

            if not record:
                return {"error": f"Record not found in {table} for user_id={user_id}" + (f", record_id={record_id}" if record_id else "")}
            

            updated_fields = []
            for field, value in updates.items():
                if hasattr(record, field):
                    setattr(record, field, value)
                    updated_fields.append(field)
                else:
                    print(f"[DB write] warning: field '{field}' doesn't exist on {table}")
            
            if not updated_fields:
                return {"error": "no valid fields to update"}
            
            session.commit()

            return {
                "success": True,
                "table": table,
                "user_id": user_id,
                "record_id": record_id,
                "updated_fields": updated_fields,
                "message": f"Updated {len(updated_fields)} fields in {table}"
            }
        except Exception as e:
            session.rollback()
            return{"error": f"DB error: {str(e)}"}
        finally:
            session.close()
    
    async def _arun(self, user_id: int, table: str, updates: Dict[str, Any], record_id: Optional[int] = None) -> Dict[str, Any]:
        return self._run(user_id, table, updates, record_id)

# tool 2: add patient records
class AddPatientRecordArgs(BaseModel):
    table: str = Field(..., description="Table to add record to")
    record_data: Dict[str, Any] = Field(..., description="Dict containing all fields needed for new record besides id which will be generated")

class AddPatientRecordTool(BaseTool):
    name: str = "add_patient_record"
    description: str = """Add a new record to the appointments table in the database
    record_data must include required fields. Do NOT include 'id' because it's auto generated upon addition
    For appointments: user_id, date (YYYY-MM-DD), time (HH:MN:SS), doctor, specialty, type, status"""
    args_schema: Type[BaseModel] = AddPatientRecordArgs
    db_connection: Any = None
    TABLE_MAP: Dict[str, Any] = {}
    
    def __init__(self, db_connection: DatabaseConnection, models: Dict[str, Any] = None):
        super().__init__()
        self.db_connection = db_connection
        self.TABLE_MAP = models or {
            "appointments": Appointment
        }
    
    def _run(self, table: str, record_data: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[DB write] adding record to {table}: {record_data}")

        # in here there's no table restrictions at all so an attacker can add fake records / harmful records etc
        if table not in self.TABLE_MAP:
            return {"error": f"Invalid table: {table}. Valid tables: {list(self.TABLE_MAP.keys())}"}
        
        # in case an id is provided, this sanitizes it
        record_data_clean = {k: v for k, v in record_data.items() if k != 'id'}
        model = self.TABLE_MAP[table]
        session = self.db_connection.get_session()

        try:
            # sanitize date and time strings
            if table == "appointments":
                if isinstance(record_data_clean.get("date"), str):
                    record_data_clean["date"] = datetime.strptime(record_data_clean["date"], "%Y-%m-%d").date()
                if isinstance(record_data_clean.get("time"), str):
                    time_str = record_data_clean["time"]
                    try:
                        record_data_clean["time"] = datetime.strptime(time_str, "%H:%M:%S").time()
                    except ValueError:
                        record_data_clean["time"] = datetime.strptime(time_str, "%H:%M").time()
            
            new_record = model(**record_data_clean)

            session.add(new_record)
            session.commit()

            # retrieve new id
            session.refresh(new_record)

            return {
                "success": True,
                "table": table,
                "record_id": new_record.id,
                "message": f"Added new record to {table} with id={new_record.id}"
            }
        
        except Exception as e:
            session.rollback()
            return {"error": f"DB error: {str(e)}"}
        finally:
            session.close()
    
    async def _arun(self, table: str, record_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._run(table, record_data)

# tool 3: delete patient records
class DeletePatientRecordArgs(BaseModel):
    user_id: Optional[int] = Field(None, description="Patient user id (optional for patients)")
    table: str = Field(..., description="Table to delete from")
    record_id: int = Field(..., description="id of the record to delete")

# tool to delete an appointment record
class DeletePatientRecordTool(BaseTool):
    name: str = "delete_appointment_record"
    description: str = """Delete a record from the appointments table in the database.
    For the appointments table: requires both user_id and record_id to identify the specific record."""
    args_schema: Type[BaseModel] = DeletePatientRecordArgs
    db_connection: Any = None
    TABLE_MAP: Dict[str, Any] = {}
    # no restrictions on what table to attack

    def __init__(self, db_connection: DatabaseConnection, models: Dict[str, Any] = None):
        super().__init__()
        self.db_connection = db_connection
        self.TABLE_MAP = models or {
            "appointments": Appointment
        }
    
    def _run(self, table: str, record_id: int, user_id: Optional[int] = None) -> Dict[str, Any]:
        print(f"[DB write] deleting from {table}: user_id={user_id}, record_id={record_id}")

        if table not in self.TABLE_MAP:
            return {"error": f"Invalid table: {table}. Valid tables: {list(self.TABLE_MAP.keys())}"}
        
        model = self.TABLE_MAP[table]
        session = self.db_connection.get_session()

        try:
            if table == "appointments":
                # for appointments use user_id and record_id
                if user_id:
                    record = session.query(model).filter_by(user_id=user_id, id=record_id).first()
            
            if not record:
                return {"error": f"Record not found: {table} with user_id={user_id}, record_id={record_id}"}
            
            session.delete(record)
            session.commit()

            return {
                "success": True,
                "table": table,
                "record_id": record_id,
                "message": f"Deleted record {record_id} from {table}"

            }
        
        except Exception as e:
            session.rollback()
            return {"error": f"DB error: {str(e)}"}
        finally:
            session.close()
    
    async def _arun(self, table: str, record_id: int, user_id: Optional[int] = None) -> Dict[str, Any]:
        return self._run(table, record_id, user_id)

# testing block
if __name__ == "__main__":
    # test db connection
    print("initializing database connection...")
    db = DatabaseConnection()
    print("\ntesting connection...")
    db.test_connection()

    print("\n" + "="*50)
    print("testing tools")
    print("\n" + "="*50)

    # test each tool
    patient_tool = QueryPatientInfoTool(db)
    print("\n1. testing QueryPatientInfoTool...")
    result = patient_tool._run(1001)
    print(f"Result: {result}")

    history_tool = QueryMedicalHistoryTool(db)
    print("\n2. testing QueryMedicalHistoryTool...")
    result = history_tool._run(1001)
    print(f"Result: {result}")

    appointments_tool = QueryAppointmentsTool(db)
    print("\n3. testing QueryAppointmentsTool...")
    result = appointments_tool._run(1001)
    print(f"Result: {result}")

    prescriptions_tool = QueryPrescriptionsTool(db)
    print("\n4. testing QueryPrescriptionsTool...")
    result = prescriptions_tool._run(1001)
    print(f"Result: {result}")

    print("\n" + "="*50)
    print("all tools tested successfully!")
    print("\n" + "="*50)