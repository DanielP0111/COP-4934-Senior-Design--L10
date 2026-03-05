-- MySQL dump 10.13  Distrib 9.6.0, for Linux (x86_64)
--
-- Host: localhost    Database: billdb
-- ------------------------------------------------------
-- Server version	9.6.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ 'bb585ad8-fd58-11f0-be24-242a6684615c:1-18';

--
-- Table structure for table `appointments`
--

DROP TABLE IF EXISTS `appointments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appointments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `date` date NOT NULL,
  `time` time NOT NULL,
  `doctor` varchar(255) DEFAULT NULL,
  `specialty` varchar(255) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `appointments_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `patients` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appointments`
--

LOCK TABLES `appointments` WRITE;
/*!40000 ALTER TABLE `appointments` DISABLE KEYS */;
INSERT INTO `appointments` VALUES (1,1001,'2025-10-20','10:00:00','Dr. Smith','Cardiology','Checkup','Scheduled'),(2,1001,'2025-09-15','14:30:00','Dr. Jones','Endocrinology','Follow-up','Completed'),(3,1001,'2025-11-05','09:00:00','Dr. Smith','Cardiology','Consultation','Scheduled'),(4,1002,'2025-10-25','11:00:00','Dr. Lee','Pulmonology','Checkup','Scheduled'),(5,1002,'2025-08-10','15:00:00','Dr. Lee','Pulmonology','Emergency','Completed'),(6,1003,'2025-10-18','13:00:00','Dr. Patel','Neurology','Checkup','Scheduled'),(7,1003,'2025-07-20','10:00:00','Dr. Patel','Neurology','Follow-up','Completed'),(8,1003,'2025-12-01','11:30:00','Dr. Patel','Neurology','Consultation','Scheduled'),(9,1004,'2025-11-10','09:30:00','Dr. Garcia','Orthopedics','Checkup','Scheduled'),(10,1004,'2025-10-05','16:00:00','Dr. Garcia','Orthopedics','Follow-up','Completed'),(11,1005,'2025-10-30','12:00:00','Dr. Kim','General Practice','Annual Physical','Scheduled'),(12,1005,'2025-09-25','10:00:00','Dr. Kim','General Practice','Checkup','Completed');
/*!40000 ALTER TABLE `appointments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medical_history`
--

DROP TABLE IF EXISTS `medical_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medical_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `conditions` text,
  `allergies` text,
  `surgeries` text,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `medical_history_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `patients` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medical_history`
--

LOCK TABLES `medical_history` WRITE;
/*!40000 ALTER TABLE `medical_history` DISABLE KEYS */;
INSERT INTO `medical_history` VALUES (1,1001,'Hypertension, Type 2 Diabetes','Penicillin','Appendectomy in 2010'),(2,1002,'Asthma','None','None'),(3,1003,'Migraines','Shellfish','Tonsillectomy in 2005'),(4,1004,'Arthritis','Pollen','Knee replacement in 2018'),(5,1005,'None','Latex','None');
/*!40000 ALTER TABLE `medical_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patients`
--

DROP TABLE IF EXISTS `patients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `patients` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `gender` varchar(50) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `phone` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `user_id_2` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patients`
--

LOCK TABLES `patients` WRITE;
/*!40000 ALTER TABLE `patients` DISABLE KEYS */;
INSERT INTO `patients` VALUES (1,1001,'Alice Johnson','1985-03-15','Female','alice@example.com','123-456-7890'),(2,1002,'Bob Smith','1978-07-22','Male','bob@example.com','234-567-8901'),(3,1003,'Carol Davis','1992-11-05','Female','carol@example.com','345-678-9012'),(4,1004,'David Wilson','1965-01-30','Male','david@example.com','456-789-0123'),(5,1005,'Eve Brown','2000-09-18','Female','eve@example.com','567-890-1234');
/*!40000 ALTER TABLE `patients` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prescriptions`
--

DROP TABLE IF EXISTS `prescriptions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prescriptions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `medication` varchar(255) DEFAULT NULL,
  `dosage` varchar(255) DEFAULT NULL,
  `frequency` varchar(255) DEFAULT NULL,
  `prescribing_doctor` varchar(255) DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `refills_remaining` int DEFAULT '0',
  `active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `prescriptions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `patients` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prescriptions`
--

LOCK TABLES `prescriptions` WRITE;
/*!40000 ALTER TABLE `prescriptions` DISABLE KEYS */;
INSERT INTO `prescriptions` VALUES (1,1001,'Lisinopril','10mg','Daily','Dr. Smith','2025-01-01',3,1),(2,1001,'Metformin','500mg','Twice daily','Dr. Jones','2024-06-15',0,0),(3,1001,'Atorvastatin','20mg','Daily','Dr. Smith','2025-02-01',5,1),(4,1002,'Albuterol Inhaler','90mcg','As needed','Dr. Lee','2023-05-10',2,1),(5,1002,'Fluticasone','50mcg','Twice daily','Dr. Lee','2024-01-01',1,1),(6,1003,'Sumatriptan','50mg','As needed','Dr. Patel','2022-11-20',4,1),(7,1003,'Propranolol','40mg','Daily','Dr. Patel','2025-03-01',0,0),(8,1004,'Ibuprofen','400mg','Three times daily','Dr. Garcia','2019-07-15',0,0),(9,1004,'Meloxicam','15mg','Daily','Dr. Garcia','2025-08-01',6,1),(10,1005,'Multivitamin','1 tablet','Daily','Dr. Kim','2024-09-01',10,1);
/*!40000 ALTER TABLE `prescriptions` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-01 19:57:30
