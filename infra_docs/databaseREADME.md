# agentic-ai-security
This README is specifically for the MySQL database container located in the compose.yaml file. The purpose of this container is to hold data to be utilized by the database AI agent, as well as function as an attack surface.

# The MySQL Database

## The Compose File
In the compose.yaml file, the following code snippet responsible for the MySQL database container is visible.

```yaml
mysql:
    build:
      context: ./startup
      dockerfile: Dockerfile.database
    image: sql-image
    container_name: mysql
    environment:
      MYSQL_ROOT_PASSWORD: pass
    ports:
      - 3307:3306
    volumes:
      - ./mysql-data:/var/lib/mysql
    networks:
      - billnet
```

- The above code snippet creates a Docker container utilizing the Dockerfile.database Dockerfile, located in the startup folder. 
- The image is named “sql-image” yet utilizes the Dockerfile to create the actual full image on startup.
- The container is simply named “mysql”
- The password to the database is set to “pass”, which may be needed later to access the database
- The container is placed upon the host’s port 3307, the standard secondary database port. The database is mapped to the container's personal port 3306.
- The volume named “mysql-data” will be used to persistently store our database’s data. This folder is initialized and populated upon startup. 
- **BEWARE:** The files automatically created upon startup will be initialized with particular privileges. As a result, a traditional user upon our server Bill will be unable to delete some of these files after the fact. This is caused by insufficient privileges for a traditional non-admin user.
- Lastly, the database is placed upon our network, named billnet, so that it may be interacted with by other containers on the network

## The Dockerfile
To help us build our MySQL image, we will utilize an associated Dockerfile. This Dockerfile is named “Dockerfile.database”. 

```dockerfile
FROM docker.io/mysql

# Copying our SQL script into this directory ensures it runs on first startup
# This will populate our DB with dummy data
COPY ./init_database.sql /docker-entrypoint-initdb.d/
```

- Inside the Dockerfile, we will simply pull the latest mysql image from docker.io as a baseline. 
- We then copy our SQL initialization script into the initialization directory
	- As a result, this script will run upon the first startup of our container, ensuring our database is properly populated with our dummy test data

## The Database Initialization Script 
This script, named “init_database.sql” is an sql script used to initialize and fill in our database.

<details>
    <summary>Click here to expand and see init_database.sql!</summary>

```sql
-- Database
CREATE DATABASE billdb;
USE billdb;

-- Tables

CREATE TABLE patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    name TEXT,
    dob DATE,
    gender TEXT,
    email TEXT,
    phone TEXT,
    INDEX(user_id)
);

CREATE TABLE medical_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    conditions TEXT,
    allergies TEXT,
    surgeries TEXT,
    FOREIGN KEY (user_id) REFERENCES patients(user_id) ON DELETE CASCADE,
    INDEX(user_id)
);

CREATE TABLE appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    doctor TEXT,
    specialty TEXT,
    type TEXT,
    status TEXT,
    FOREIGN KEY (user_id) REFERENCES patients(user_id) ON DELETE CASCADE,
    INDEX(user_id)
);

CREATE TABLE prescriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    medication TEXT,
    dosage TEXT,
    frequency TEXT,
    prescribing_doctor TEXT,
    start_date DATE,
    refills_remaining INT DEFAULT 0,
    active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES patients(user_id) ON DELETE CASCADE,
    INDEX(user_id)
);

-- SAMPLE DATA

INSERT INTO patients (user_id, name, dob, gender, email, phone) VALUES
(1001, 'Alice Johnson', '1985-03-15', 'Female', 'alice@example.com', '123-456-7890'),
(1002, 'Bob Smith', '1978-07-22', 'Male', 'bob@example.com', '234-567-8901'),
(1003, 'Carol Davis', '1992-11-05', 'Female', 'carol@example.com', '345-678-9012'),
(1004, 'David Wilson', '1965-01-30', 'Male', 'david@example.com', '456-789-0123'),
(1005, 'Eve Brown', '2000-09-18', 'Female', 'eve@example.com', '567-890-1234');

INSERT INTO medical_history (user_id, conditions, allergies, surgeries) VALUES
(1001, 'Hypertension, Type 2 Diabetes', 'Penicillin', 'Appendectomy in 2010'),
(1002, 'Asthma', 'None', 'None'),
(1003, 'Migraines', 'Shellfish', 'Tonsillectomy in 2005'),
(1004, 'Arthritis', 'Pollen', 'Knee replacement in 2018'),
(1005, 'None', 'Latex', 'None');

INSERT INTO appointments (user_id, date, time, doctor, specialty, type, status) VALUES
(1001, '2025-10-20', '10:00:00', 'Dr. Smith', 'Cardiology', 'Checkup', 'Scheduled'),
(1001, '2025-09-15', '14:30:00', 'Dr. Jones', 'Endocrinology', 'Follow-up', 'Completed'),
(1001, '2025-11-05', '09:00:00', 'Dr. Smith', 'Cardiology', 'Consultation', 'Scheduled'),

(1002, '2025-10-25', '11:00:00', 'Dr. Lee', 'Pulmonology', 'Checkup', 'Scheduled'),
(1002, '2025-08-10', '15:00:00', 'Dr. Lee', 'Pulmonology', 'Emergency', 'Completed'),

(1003, '2025-10-18', '13:00:00', 'Dr. Patel', 'Neurology', 'Checkup', 'Scheduled'),
(1003, '2025-07-20', '10:00:00', 'Dr. Patel', 'Neurology', 'Follow-up', 'Completed'),
(1003, '2025-12-01', '11:30:00', 'Dr. Patel', 'Neurology', 'Consultation', 'Scheduled'),

(1004, '2025-11-10', '09:30:00', 'Dr. Garcia', 'Orthopedics', 'Checkup', 'Scheduled'),
(1004, '2025-10-05', '16:00:00', 'Dr. Garcia', 'Orthopedics', 'Follow-up', 'Completed'),

(1005, '2025-10-30', '12:00:00', 'Dr. Kim', 'General Practice', 'Annual Physical', 'Scheduled'),
(1005, '2025-09-25', '10:00:00', 'Dr. Kim', 'General Practice', 'Checkup', 'Completed');

INSERT INTO prescriptions (user_id, medication, dosage, frequency, prescribing_doctor, start_date, refills_remaining, active) VALUES
(1001, 'Lisinopril', '10mg', 'Daily', 'Dr. Smith', '2025-01-01', 3, TRUE),
(1001, 'Metformin', '500mg', 'Twice daily', 'Dr. Jones', '2024-06-15', 0, FALSE),
(1001, 'Atorvastatin', '20mg', 'Daily', 'Dr. Smith', '2025-02-01', 5, TRUE),

(1002, 'Albuterol Inhaler', '90mcg', 'As needed', 'Dr. Lee', '2023-05-10', 2, TRUE),
(1002, 'Fluticasone', '50mcg', 'Twice daily', 'Dr. Lee', '2024-01-01', 1, TRUE),

(1003, 'Sumatriptan', '50mg', 'As needed', 'Dr. Patel', '2022-11-20', 4, TRUE),
(1003, 'Propranolol', '40mg', 'Daily', 'Dr. Patel', '2025-03-01', 0, FALSE),

(1004, 'Ibuprofen', '400mg', 'Three times daily', 'Dr. Garcia', '2019-07-15', 0, FALSE),
(1004, 'Meloxicam', '15mg', 'Daily', 'Dr. Garcia', '2025-08-01', 6, TRUE),

(1005, 'Multivitamin', '1 tablet', 'Daily', 'Dr. Kim', '2024-09-01', 10, TRUE);
```

</details>

- Firstly, the main database named “billdb” is created and set to the active database
- The tables for patients, medical history, appointments, and prescriptions are then created and initialized
- Lastly, the freshly created tables are then populated with sample dummy data to be utilized by our agentic healthcare chatbot system.

## Accessing the container
After running the following code to startup all of the containers in the compose file:
```bash
docker compose up -d
```
You may enter into the MySQL container bash shell by running the following command:
 ```bash
docker exec -it mysql bash
```
Once inside the container bash shell, you can access the database itself by simply entering:
 ```bash
mysql
```
If you encounter an error regarding access being denied, try this instead:
 ```bash
mysql -ppass
```
The above line will enter the password of “pass” as you attempt to access the database, ensuring your access is not denied.

From there, you may use traditional MySQL commands to navigate and alter the database.

To exit, simply enter:
```bash
exit
```
