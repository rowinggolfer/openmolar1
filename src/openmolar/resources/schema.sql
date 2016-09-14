-- MySQL dump 10.15  Distrib 10.0.26-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: openmolar_demo
-- ------------------------------------------------------
-- Server version	10.0.26-MariaDB-3

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `aday`
--

DROP TABLE IF EXISTS `aday`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aday` (
  `adate` date NOT NULL DEFAULT '0000-00-00',
  `apptix` smallint(6) NOT NULL DEFAULT '0',
  `start` smallint(6) DEFAULT NULL,
  `end` smallint(6) DEFAULT NULL,
  `flag` tinyint(4) DEFAULT NULL,
  `memo` char(30) DEFAULT NULL,
  PRIMARY KEY (`adate`,`apptix`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aday`
--

LOCK TABLES `aday` WRITE;
/*!40000 ALTER TABLE `aday` DISABLE KEYS */;
/*!40000 ALTER TABLE `aday` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`openmolar`@`localhost`*/ /*!50003 TRIGGER aday_update_trigger 
    BEFORE UPDATE ON aday 
    FOR EACH ROW 
        BEGIN 
            DECLARE clash_count INT; 
            IF NEW.flag = 0 THEN
                SET clash_count=(SELECT count(*) FROM aslot WHERE apptix=NEW.apptix AND adate=NEW.adate AND serialno!=0); 
                IF clash_count>0 THEN 
                    SIGNAL SQLSTATE '45000' 
                    SET message_text="existing appointments prevent you blocking this day"; 
                END IF;
            ELSE
                SET clash_count=(SELECT count(*) FROM aslot 
                WHERE apptix=NEW.apptix AND adate=NEW.adate AND (start<NEW.start OR end>NEW.end)); 
            
                IF clash_count>0 THEN 
                    SIGNAL SQLSTATE '45000' 
                    SET message_text="existing appointments prevent you changing this day"; 
                END IF;
            END IF;
        END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `appt_prefs`
--

DROP TABLE IF EXISTS `appt_prefs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `appt_prefs` (
  `serialno` int(11) NOT NULL DEFAULT '0',
  `recall_active` tinyint(1) NOT NULL DEFAULT '1',
  `recdent_period` int(11) DEFAULT NULL,
  `recdent` date DEFAULT NULL,
  `rechyg_period` int(11) DEFAULT NULL,
  `rechyg` date DEFAULT NULL,
  `recall_method` enum('post','sms','email','tel') DEFAULT NULL,
  `sms_reminders` tinyint(1) NOT NULL DEFAULT '0',
  `no_combined_appts` tinyint(1) NOT NULL DEFAULT '0',
  `note` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`serialno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appt_prefs`
--

LOCK TABLES `appt_prefs` WRITE;
/*!40000 ALTER TABLE `appt_prefs` DISABLE KEYS */;
/*!40000 ALTER TABLE `appt_prefs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `apr`
--

DROP TABLE IF EXISTS `apr`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `apr` (
  `serialno` int(11) NOT NULL DEFAULT '0',
  `aprix` tinyint(4) NOT NULL DEFAULT '0',
  `practix` smallint(6) DEFAULT NULL,
  `code0` char(8) DEFAULT NULL,
  `code1` char(8) DEFAULT NULL,
  `code2` char(8) DEFAULT NULL,
  `note` char(20) DEFAULT NULL,
  `adate` date DEFAULT NULL,
  `atime` smallint(6) DEFAULT NULL,
  `length` smallint(6) DEFAULT NULL,
  `flag0` tinyint(4) DEFAULT NULL,
  `flag1` tinyint(4) DEFAULT NULL,
  `flag2` tinyint(4) DEFAULT NULL,
  `flag3` tinyint(4) DEFAULT NULL,
  `flag4` tinyint(4) DEFAULT NULL,
  `datespec` char(10) DEFAULT NULL,
  PRIMARY KEY (`serialno`,`aprix`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `apr`
--

LOCK TABLES `apr` WRITE;
/*!40000 ALTER TABLE `apr` DISABLE KEYS */;
/*!40000 ALTER TABLE `apr` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `aslot`
--

DROP TABLE IF EXISTS `aslot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aslot` (
  `adate` date DEFAULT NULL,
  `apptix` smallint(6) DEFAULT NULL,
  `start` smallint(6) DEFAULT NULL,
  `end` smallint(6) DEFAULT NULL,
  `name` char(30) DEFAULT NULL,
  `serialno` int(11) DEFAULT NULL,
  `code0` char(8) DEFAULT NULL,
  `code1` char(8) DEFAULT NULL,
  `code2` char(8) DEFAULT NULL,
  `note` char(20) DEFAULT NULL,
  `flag0` tinyint(4) DEFAULT NULL,
  `flag1` tinyint(4) DEFAULT NULL,
  `flag2` tinyint(4) DEFAULT NULL,
  `flag3` tinyint(4) DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY `adate` (`adate`,`apptix`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aslot`
--

LOCK TABLES `aslot` WRITE;
/*!40000 ALTER TABLE `aslot` DISABLE KEYS */;
/*!40000 ALTER TABLE `aslot` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`openmolar`@`localhost`*/ /*!50003 TRIGGER aslot_trigger 
    BEFORE INSERT ON aslot
    FOR EACH ROW
    BEGIN 
        DECLARE appt_count INT;
        if NEW.start = NEW.end then
            SET appt_count = 0;
        else
            SET appt_count = (
                SELECT count(*) from aslot 
                where adate=NEW.adate and start>=NEW.start and start<NEW.end and apptix=NEW.apptix
                );
        end if;
        
        if appt_count>0 then
            signal sqlstate '45000' 
            set message_text = "this appointment clashes with one (or more) already in the database";
        end if; 
            
    END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `bpe`
--

DROP TABLE IF EXISTS `bpe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bpe` (
  `serialno` int(11) NOT NULL DEFAULT '0',
  `bpedate` date NOT NULL DEFAULT '0000-00-00',
  `bpe` char(6) DEFAULT NULL,
  PRIMARY KEY (`serialno`,`bpedate`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bpe`
--

LOCK TABLES `bpe` WRITE;
/*!40000 ALTER TABLE `bpe` DISABLE KEYS */;
/*!40000 ALTER TABLE `bpe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `calendar`
--

DROP TABLE IF EXISTS `calendar`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `calendar` (
  `adate` date NOT NULL,
  `memo` char(30) DEFAULT NULL,
  PRIMARY KEY (`adate`),
  KEY `adate` (`adate`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `calendar`
--

LOCK TABLES `calendar` WRITE;
/*!40000 ALTER TABLE `calendar` DISABLE KEYS */;
/*!40000 ALTER TABLE `calendar` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `calldurr`
--

DROP TABLE IF EXISTS `calldurr`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `calldurr` (
  `stn` tinyint(4) NOT NULL DEFAULT '0',
  `serialno` int(11) DEFAULT NULL,
  PRIMARY KEY (`stn`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `calldurr`
--

LOCK TABLES `calldurr` WRITE;
/*!40000 ALTER TABLE `calldurr` DISABLE KEYS */;
/*!40000 ALTER TABLE `calldurr` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cashbook`
--

DROP TABLE IF EXISTS `cashbook`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cashbook` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cbdate` date DEFAULT NULL,
  `ref` char(10) DEFAULT NULL,
  `linkid` int(11) DEFAULT NULL,
  `descr` varchar(32) DEFAULT NULL,
  `code` tinyint(3) unsigned DEFAULT NULL,
  `dntid` smallint(6) DEFAULT NULL,
  `amt` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `date` (`cbdate`),
  KEY `ref` (`ref`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cashbook`
--

LOCK TABLES `cashbook` WRITE;
/*!40000 ALTER TABLE `cashbook` DISABLE KEYS */;
/*!40000 ALTER TABLE `cashbook` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cbcodes`
--

DROP TABLE IF EXISTS `cbcodes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cbcodes` (
  `code` tinyint(3) unsigned DEFAULT NULL,
  `flag` tinyint(4) DEFAULT NULL,
  `descr` char(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cbcodes`
--

LOCK TABLES `cbcodes` WRITE;
/*!40000 ALTER TABLE `cbcodes` DISABLE KEYS */;
INSERT INTO `cbcodes` VALUES (1,2,'NHS CASH'),(2,2,'PRIVATE CASH'),(3,2,'NHS CHEQUE'),(4,2,'PRIVATE CHEQUE'),(5,2,'NHS CARD'),(6,2,'PRIVATE CARD'),(9,2,'BANK TRANSFER'),(14,2,'SUNDRY CASH'),(15,2,'SUNDRY CHEQUE'),(17,2,'SUNDRY CARD'),(21,2,'ANNUAL HDP'),(24,2,'OTHER'),(125,2,'REFUND');
/*!40000 ALTER TABLE `cbcodes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `claims`
--

DROP TABLE IF EXISTS `claims`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `claims` (
  `courseno` int(11) NOT NULL DEFAULT '0',
  `serialno` int(11) NOT NULL DEFAULT '0',
  `dntix` smallint(6) DEFAULT '0',
  `proddate` date DEFAULT NULL,
  `startdate` date DEFAULT NULL,
  `cmpldate` date DEFAULT NULL,
  `regdate` date DEFAULT NULL,
  `authdate` date DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `sname` varchar(30) DEFAULT NULL,
  `fname` varchar(30) DEFAULT NULL,
  `addr1` varchar(30) DEFAULT NULL,
  `addr2` varchar(30) DEFAULT NULL,
  `addr3` varchar(30) DEFAULT NULL,
  `pcde` varchar(30) DEFAULT NULL,
  `nhsno` varchar(30) DEFAULT NULL,
  `prevsname` varchar(30) DEFAULT NULL,
  `exempttext` varchar(50) DEFAULT NULL,
  `i0` int(11) DEFAULT '0',
  `i1` int(11) DEFAULT '0',
  `i2` int(11) DEFAULT '0',
  `i3` int(11) DEFAULT '0',
  `i4` int(11) DEFAULT '0',
  `f0` tinyint(3) unsigned DEFAULT '0',
  `f1` tinyint(3) unsigned DEFAULT '0',
  `f2` tinyint(3) unsigned DEFAULT '0',
  `f3` tinyint(3) unsigned DEFAULT '0',
  `f4` tinyint(3) unsigned DEFAULT '0',
  `f5` tinyint(3) unsigned DEFAULT '0',
  `f6` tinyint(3) unsigned DEFAULT '0',
  `f7` tinyint(3) unsigned DEFAULT '0',
  `f8` tinyint(3) unsigned DEFAULT '0',
  `f9` tinyint(3) unsigned DEFAULT '0',
  `submstatus` tinyint(4) DEFAULT '0',
  `submcount` tinyint(4) DEFAULT '0',
  `submno` int(11) DEFAULT '0',
  `claimdata` blob,
  `trtdata` blob,
  `archdate` date DEFAULT NULL,
  `town` varchar(30) DEFAULT NULL,
  `county` varchar(30) DEFAULT NULL,
  `regtype` tinyint(3) unsigned DEFAULT '0',
  PRIMARY KEY (`serialno`,`courseno`),
  KEY `dentist` (`dntix`),
  KEY `patient` (`sname`,`fname`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `claims`
--

LOCK TABLES `claims` WRITE;
/*!40000 ALTER TABLE `claims` DISABLE KEYS */;
/*!40000 ALTER TABLE `claims` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clinical_memos`
--

DROP TABLE IF EXISTS `clinical_memos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `clinical_memos` (
  `ix` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `serialno` int(11) unsigned NOT NULL,
  `author` char(8) DEFAULT NULL,
  `datestamp` datetime NOT NULL,
  `hidden` tinyint(1) NOT NULL DEFAULT '0',
  `synopsis` text,
  PRIMARY KEY (`ix`),
  KEY `serialno` (`serialno`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clinical_memos`
--

LOCK TABLES `clinical_memos` WRITE;
/*!40000 ALTER TABLE `clinical_memos` DISABLE KEYS */;
INSERT INTO `clinical_memos` VALUES (1,1,'REC','2014-06-10 20:28:10',0,'This patient is for demonstration purposes only. Any similarity to any person, alive or dead, is entirely unintentional.');
/*!40000 ALTER TABLE `clinical_memos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clinician_dates`
--

DROP TABLE IF EXISTS `clinician_dates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `clinician_dates` (
  `clinician_ix` smallint(5) unsigned NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date DEFAULT NULL,
  `date_comments` varchar(255) DEFAULT NULL,
  KEY `clinician_ix` (`clinician_ix`),
  CONSTRAINT `clinician_dates_ibfk_1` FOREIGN KEY (`clinician_ix`) REFERENCES `clinicians` (`ix`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clinician_dates`
--

LOCK TABLES `clinician_dates` WRITE;
/*!40000 ALTER TABLE `clinician_dates` DISABLE KEYS */;
/*!40000 ALTER TABLE `clinician_dates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clinicians`
--

DROP TABLE IF EXISTS `clinicians`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `clinicians` (
  `ix` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `initials` char(5) NOT NULL,
  `name` varchar(64) NOT NULL,
  `formal_name` varchar(128) DEFAULT NULL,
  `qualifications` varchar(64) DEFAULT NULL,
  `type` smallint(5) NOT NULL DEFAULT '1',
  `speciality` varchar(64) DEFAULT NULL,
  `data` varchar(255) DEFAULT NULL,
  `comments` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ix`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clinicians`
--

LOCK TABLES `clinicians` WRITE;
/*!40000 ALTER TABLE `clinicians` DISABLE KEYS */;
/*!40000 ALTER TABLE `clinicians` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `currtrtmt2`
--

DROP TABLE IF EXISTS `currtrtmt2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `currtrtmt2` (
  `courseno` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `serialno` int(11) DEFAULT NULL,
  `examt` varchar(10) NOT NULL DEFAULT '',
  `examd` date DEFAULT NULL,
  `accd` date DEFAULT NULL,
  `cmpd` date DEFAULT NULL,
  `xraypl` varchar(56) NOT NULL DEFAULT '',
  `periopl` varchar(56) NOT NULL DEFAULT '',
  `anaespl` varchar(56) NOT NULL DEFAULT '',
  `otherpl` varchar(56) NOT NULL DEFAULT '',
  `ndupl` varchar(56) NOT NULL DEFAULT '',
  `ndlpl` varchar(56) NOT NULL DEFAULT '',
  `odupl` varchar(56) NOT NULL DEFAULT '',
  `odlpl` varchar(56) NOT NULL DEFAULT '',
  `custompl` varchar(56) NOT NULL DEFAULT '',
  `ur8pl` varchar(34) NOT NULL DEFAULT '',
  `ur7pl` varchar(34) NOT NULL DEFAULT '',
  `ur6pl` varchar(34) NOT NULL DEFAULT '',
  `ur5pl` varchar(34) NOT NULL DEFAULT '',
  `ur4pl` varchar(34) NOT NULL DEFAULT '',
  `ur3pl` varchar(34) NOT NULL DEFAULT '',
  `ur2pl` varchar(34) NOT NULL DEFAULT '',
  `ur1pl` varchar(34) NOT NULL DEFAULT '',
  `ul1pl` varchar(34) NOT NULL DEFAULT '',
  `ul2pl` varchar(34) NOT NULL DEFAULT '',
  `ul3pl` varchar(34) NOT NULL DEFAULT '',
  `ul4pl` varchar(34) NOT NULL DEFAULT '',
  `ul5pl` varchar(34) NOT NULL DEFAULT '',
  `ul6pl` varchar(34) NOT NULL DEFAULT '',
  `ul7pl` varchar(34) NOT NULL DEFAULT '',
  `ul8pl` varchar(34) NOT NULL DEFAULT '',
  `ll8pl` varchar(34) NOT NULL DEFAULT '',
  `ll7pl` varchar(34) NOT NULL DEFAULT '',
  `ll6pl` varchar(34) NOT NULL DEFAULT '',
  `ll5pl` varchar(34) NOT NULL DEFAULT '',
  `ll4pl` varchar(34) NOT NULL DEFAULT '',
  `ll3pl` varchar(34) NOT NULL DEFAULT '',
  `ll2pl` varchar(34) NOT NULL DEFAULT '',
  `ll1pl` varchar(34) NOT NULL DEFAULT '',
  `lr1pl` varchar(34) NOT NULL DEFAULT '',
  `lr2pl` varchar(34) NOT NULL DEFAULT '',
  `lr3pl` varchar(34) NOT NULL DEFAULT '',
  `lr4pl` varchar(34) NOT NULL DEFAULT '',
  `lr5pl` varchar(34) NOT NULL DEFAULT '',
  `lr6pl` varchar(34) NOT NULL DEFAULT '',
  `lr7pl` varchar(34) NOT NULL DEFAULT '',
  `lr8pl` varchar(34) NOT NULL DEFAULT '',
  `ur8cmp` varchar(34) NOT NULL DEFAULT '',
  `ur7cmp` varchar(34) NOT NULL DEFAULT '',
  `ur6cmp` varchar(34) NOT NULL DEFAULT '',
  `ur5cmp` varchar(34) NOT NULL DEFAULT '',
  `ur4cmp` varchar(34) NOT NULL DEFAULT '',
  `ur3cmp` varchar(34) NOT NULL DEFAULT '',
  `ur2cmp` varchar(34) NOT NULL DEFAULT '',
  `ur1cmp` varchar(34) NOT NULL DEFAULT '',
  `ul1cmp` varchar(34) NOT NULL DEFAULT '',
  `ul2cmp` varchar(34) NOT NULL DEFAULT '',
  `ul3cmp` varchar(34) NOT NULL DEFAULT '',
  `ul4cmp` varchar(34) NOT NULL DEFAULT '',
  `ul5cmp` varchar(34) NOT NULL DEFAULT '',
  `ul6cmp` varchar(34) NOT NULL DEFAULT '',
  `ul7cmp` varchar(34) NOT NULL DEFAULT '',
  `ul8cmp` varchar(34) NOT NULL DEFAULT '',
  `ll8cmp` varchar(34) NOT NULL DEFAULT '',
  `ll7cmp` varchar(34) NOT NULL DEFAULT '',
  `ll6cmp` varchar(34) NOT NULL DEFAULT '',
  `ll5cmp` varchar(34) NOT NULL DEFAULT '',
  `ll4cmp` varchar(34) NOT NULL DEFAULT '',
  `ll3cmp` varchar(34) NOT NULL DEFAULT '',
  `ll2cmp` varchar(34) NOT NULL DEFAULT '',
  `ll1cmp` varchar(34) NOT NULL DEFAULT '',
  `lr1cmp` varchar(34) NOT NULL DEFAULT '',
  `lr2cmp` varchar(34) NOT NULL DEFAULT '',
  `lr3cmp` varchar(34) NOT NULL DEFAULT '',
  `lr4cmp` varchar(34) NOT NULL DEFAULT '',
  `lr5cmp` varchar(34) NOT NULL DEFAULT '',
  `lr6cmp` varchar(34) NOT NULL DEFAULT '',
  `lr7cmp` varchar(34) NOT NULL DEFAULT '',
  `lr8cmp` varchar(34) NOT NULL DEFAULT '',
  `xraycmp` varchar(56) NOT NULL DEFAULT '',
  `periocmp` varchar(56) NOT NULL DEFAULT '',
  `anaescmp` varchar(56) NOT NULL DEFAULT '',
  `othercmp` varchar(56) NOT NULL DEFAULT '',
  `nducmp` varchar(56) NOT NULL DEFAULT '',
  `ndlcmp` varchar(56) NOT NULL DEFAULT '',
  `oducmp` varchar(56) NOT NULL DEFAULT '',
  `odlcmp` varchar(56) NOT NULL DEFAULT '',
  `customcmp` varchar(56) NOT NULL DEFAULT '',
  `ftr` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`courseno`),
  KEY `serialno` (`serialno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `currtrtmt2`
--

LOCK TABLES `currtrtmt2` WRITE;
/*!40000 ALTER TABLE `currtrtmt2` DISABLE KEYS */;
/*!40000 ALTER TABLE `currtrtmt2` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `daybook`
--

DROP TABLE IF EXISTS `daybook`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `daybook` (
  `date` date DEFAULT NULL,
  `serialno` int(11) DEFAULT NULL,
  `coursetype` char(1) DEFAULT NULL,
  `dntid` smallint(6) DEFAULT NULL,
  `trtid` smallint(6) DEFAULT NULL,
  `diagn` varchar(56) DEFAULT NULL,
  `perio` varchar(56) DEFAULT NULL,
  `anaes` varchar(56) DEFAULT NULL,
  `misc` varchar(56) DEFAULT NULL,
  `ndu` varchar(56) DEFAULT NULL,
  `ndl` varchar(56) DEFAULT NULL,
  `odu` varchar(56) DEFAULT NULL,
  `odl` varchar(56) DEFAULT NULL,
  `other` varchar(56) DEFAULT NULL,
  `chart` blob,
  `feesa` int(11) DEFAULT NULL,
  `feesb` int(11) DEFAULT NULL,
  `feesc` int(11) DEFAULT NULL,
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  KEY `date` (`date`),
  KEY `serialno` (`serialno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `daybook`
--

LOCK TABLES `daybook` WRITE;
/*!40000 ALTER TABLE `daybook` DISABLE KEYS */;
/*!40000 ALTER TABLE `daybook` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `daybook_link`
--

DROP TABLE IF EXISTS `daybook_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `daybook_link` (
  `ix` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `daybook_id` int(11) DEFAULT NULL,
  `tx_hash` char(40) NOT NULL,
  PRIMARY KEY (`ix`),
  KEY `daybook_id` (`daybook_id`),
  KEY `daybook_id_index` (`tx_hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `daybook_link`
--

LOCK TABLES `daybook_link` WRITE;
/*!40000 ALTER TABLE `daybook_link` DISABLE KEYS */;
/*!40000 ALTER TABLE `daybook_link` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `diary_link`
--

DROP TABLE IF EXISTS `diary_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `diary_link` (
  `clinician_ix` smallint(5) unsigned NOT NULL,
  `apptix` smallint(5) unsigned NOT NULL,
  KEY `clinician_ix` (`clinician_ix`),
  CONSTRAINT `diary_link_ibfk_1` FOREIGN KEY (`clinician_ix`) REFERENCES `clinicians` (`ix`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `diary_link`
--

LOCK TABLES `diary_link` WRITE;
/*!40000 ALTER TABLE `diary_link` DISABLE KEYS */;
/*!40000 ALTER TABLE `diary_link` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `docsimported`
--

DROP TABLE IF EXISTS `docsimported`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `docsimported` (
  `ix` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `serialno` int(11) unsigned NOT NULL DEFAULT '0',
  `datatype` varchar(60) NOT NULL DEFAULT 'application/octet-stream',
  `name` varchar(120) NOT NULL DEFAULT '',
  `size` bigint(20) unsigned NOT NULL DEFAULT '1024',
  `filedate` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `importime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ix`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `docsimported`
--

LOCK TABLES `docsimported` WRITE;
/*!40000 ALTER TABLE `docsimported` DISABLE KEYS */;
/*!40000 ALTER TABLE `docsimported` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `docsimporteddata`
--

DROP TABLE IF EXISTS `docsimporteddata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `docsimporteddata` (
  `ix` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `masterid` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `filedata` blob NOT NULL,
  PRIMARY KEY (`ix`),
  KEY `master_idx` (`masterid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `docsimporteddata`
--

LOCK TABLES `docsimporteddata` WRITE;
/*!40000 ALTER TABLE `docsimporteddata` DISABLE KEYS */;
/*!40000 ALTER TABLE `docsimporteddata` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `est_link2`
--

DROP TABLE IF EXISTS `est_link2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `est_link2` (
  `ix` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `est_id` int(11) DEFAULT NULL,
  `tx_hash` char(40) NOT NULL,
  `completed` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`ix`),
  KEY `est_id` (`est_id`),
  KEY `est_link2_hash_index` (`tx_hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `est_link2`
--

LOCK TABLES `est_link2` WRITE;
/*!40000 ALTER TABLE `est_link2` DISABLE KEYS */;
/*!40000 ALTER TABLE `est_link2` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `est_logger`
--

DROP TABLE IF EXISTS `est_logger`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `est_logger` (
  `ix` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `courseno` int(11) unsigned NOT NULL,
  `est_data` mediumtext NOT NULL,
  `operator` varchar(16) NOT NULL,
  `time_stamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ix`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `est_logger`
--

LOCK TABLES `est_logger` WRITE;
/*!40000 ALTER TABLE `est_logger` DISABLE KEYS */;
/*!40000 ALTER TABLE `est_logger` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exemptions`
--

DROP TABLE IF EXISTS `exemptions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `exemptions` (
  `ix` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `serialno` int(11) unsigned NOT NULL,
  `exemption` varchar(10) DEFAULT NULL,
  `exempttext` varchar(50) DEFAULT NULL,
  `datestamp` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`ix`),
  KEY `serialno` (`serialno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exemptions`
--

LOCK TABLES `exemptions` WRITE;
/*!40000 ALTER TABLE `exemptions` DISABLE KEYS */;
/*!40000 ALTER TABLE `exemptions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `families`
--

DROP TABLE IF EXISTS `families`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `families` (
  `familyno` int(11) NOT NULL,
  `head` int(11) DEFAULT NULL,
  PRIMARY KEY (`familyno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `families`
--

LOCK TABLES `families` WRITE;
/*!40000 ALTER TABLE `families` DISABLE KEYS */;
/*!40000 ALTER TABLE `families` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feescales`
--

DROP TABLE IF EXISTS `feescales`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `feescales` (
  `ix` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `in_use` tinyint(1) NOT NULL DEFAULT '0',
  `priority` int(8) DEFAULT NULL,
  `comment` varchar(255) NOT NULL DEFAULT 'unnamed feescale',
  `xml_data` mediumtext NOT NULL,
  PRIMARY KEY (`ix`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feescales`
--

LOCK TABLES `feescales` WRITE;
/*!40000 ALTER TABLE `feescales` DISABLE KEYS */;
INSERT INTO `feescales` VALUES (1,1,0,'example feescale','<?xml version=\"1.0\" ?><feescale>\n	<version>0.1</version>\n	<tablename>test_feescale</tablename>\n	<feescale_description>Example Fee Scale</feescale_description>\n	<category>P</category>\n	<header id=\"1\">Diagnosis</header>\n	<header id=\"2\">Preventive Care</header>\n	<header id=\"3\">Periodontal Treatment</header>\n	<header id=\"4\">Conservative Treatment</header>\n	<header id=\"5\">Endodontic Treatment</header>\n	<header id=\"6\">Crowns and Veneers</header>\n	<header id=\"7\">Bridgework</header>\n	<header id=\"8\">Extractions and Surgical Treatment</header>\n	<header id=\"9\">Prostheses</header>\n	<header id=\"10\">Orthodontic Treatment</header>\n	<header id=\"11\">Other Forms of Treatment</header>\n	<start>\n		<year>2013</year>\n		<month>8</month>\n		<day>1</day>\n	</start>\n	<item id=\"E0101\">\n		<section>1</section>\n		<shortcut att=\"exam\">CE</shortcut>\n		<description>clinical examination^</description>\n		<fee>\n			<brief_description>clinical exam</brief_description>\n			<gross>2200</gross>\n			<charge>2200</charge>\n		</fee>\n	</item>\n	<item id=\"E0111\">\n		<section>1</section>\n		<shortcut att=\"exam\">ECE</shortcut>\n		<description>extensive clinical examination^</description>\n		<fee>\n			<brief_description>extensive clinical exam</brief_description>\n			<gross>4500</gross>\n			<charge>4500</charge>\n		</fee>\n	</item>\n	<item id=\"E0121\" obscurity=\"2\">\n		<section>1</section>\n		<shortcut att=\"exam\">FCA</shortcut>\n		<description>full case assessment^</description>\n		<fee>\n			<brief_description>full case assessment^</brief_description>\n			<gross>6000</gross>\n			<charge>6000</charge>\n		</fee>\n	</item>\n	<item id=\"E0201\">\n		<section>1</section>\n		<shortcut att=\"xray\">S</shortcut>\n		<description>small xray*</description>\n		<fee condition=\"item_no=1\">\n			<brief_description>small xrays 1 film</brief_description>\n			<gross>900</gross>\n			<charge>900</charge>\n		</fee>\n		<fee condition=\"item_no=2\">\n			<brief_description>small xrays 2 films</brief_description>\n			<gross>1500</gross>\n			<charge>1500</charge>\n		</fee>\n		<fee condition=\"item_no=3\">\n			<brief_description>small xrays 3 films</brief_description>\n			<gross>2000</gross>\n			<charge>2000</charge>\n		</fee>\n		<fee condition=\"item_no&gt;=4\">\n			<brief_description>small xrays maximum</brief_description>\n			<gross>2500</gross>\n			<charge>2500</charge>\n		</fee>\n	</item>\n	<item id=\"E1401\" obscurity=\"0\">\n		<section>4</section>\n		<shortcut att=\"chart\" type=\"regex\">u[lr][de4-8][MODBP]*$|l[lr][de4-8][MODBL]*$|u[lr][a-c1-3][MIDBP]*$|l[lr][a-c1-3][MIDBL]*$</shortcut>\n		<description>filling*</description>\n		<fee>\n			<brief_description>filling</brief_description>\n			<gross>4500</gross>\n			<charge>4500</charge>\n		</fee>\n	</item>\n	<item id=\"E1001\">\n		<section>3</section>\n		<shortcut att=\"perio\">SP</shortcut>\n		<description>scale and polish^</description>\n		<fee>\n			<brief_description>scale &amp; polish</brief_description>\n			<gross>3300</gross>\n			<charge>3300</charge>\n		</fee>\n		<feescale_forbid>\n			<reason>please add scale and polish to a treatment plan conventionally</reason>\n		</feescale_forbid>\n	</item>\n	<item id=\"E1011\">\n		<section>3</section>\n		<shortcut att=\"perio\">SP+</shortcut>\n		<description>extended scale and polish^</description>\n		<fee>\n			<brief_description>scale &amp; polish &gt; 1 visit</brief_description>\n			<gross>4500</gross>\n			<charge>4500</charge>\n		</fee>\n	</item>\n	<item id=\"E1501\">\n		<section>5</section>\n		<shortcut att=\"chart\" type=\"regex\">[ul][lr][1-3]RT$</shortcut>\n		<description>anterior root filling*</description>\n		<fee>\n			<brief_description>root filling 1-3</brief_description>\n			<gross>19500</gross>\n			<charge>19500</charge>\n		</fee>\n	</item>\n	<item id=\"E1502\">\n		<section>5</section>\n		<shortcut att=\"chart\" type=\"regex\">[ul][lr][45]RT$</shortcut>\n		<description>premolar root filling*</description>\n		<fee>\n			<brief_description>root filling 4-5</brief_description>\n			<gross>19500</gross>\n			<charge>19500</charge>\n		</fee>\n	</item>\n	<item id=\"E1504\">\n		<section>5</section>\n		<shortcut att=\"chart\" type=\"regex\">[ul][lr][6-8]RT$</shortcut>\n		<description>molar root filling*</description>\n		<fee>\n			<brief_description>root filling 6-8</brief_description>\n			<gross>28000</gross>\n			<charge>19500</charge>\n		</fee>\n	</item>\n	<item id=\"E0601\">\n		<section>6</section>\n		<shortcut att=\"chart\" type=\"regex\">[ul][lr][1-8]CR</shortcut>\n		<description>other crown*</description>\n		<fee>\n			<brief_description>unspecified crown</brief_description>\n			<gross>35000</gross>\n			<charge>0</charge>\n		</fee>\n	</item>\n	<item id=\"E0701\">\n		<section>7</section>\n		<shortcut att=\"chart\" type=\"regex\">[ul][lr][1-8]BR</shortcut>\n		<description>bridge unit*</description>\n		<fee>\n			<brief_description>unspecified bridge unit</brief_description>\n			<gross>35000</gross>\n			<charge>0</charge>\n		</fee>\n	</item>\n	<item id=\"E2101\">\n		<section>8</section>\n		<shortcut att=\"chart\" type=\"regex\">u[lr][a-e1-8]EX</shortcut>\n		<description>extraction*</description>\n		<fee condition=\"item_no=1\">\n			<brief_description>extraction, 1 tooth</brief_description>\n			<gross>5500</gross>\n			<charge>5500</charge>\n		</fee>\n		<fee condition=\"item_no=2\">\n			<brief_description>extraction, 2 teeth</brief_description>\n			<gross>6500</gross>\n			<charge>5500</charge>\n		</fee>\n		<fee condition=\"3&lt;=item_no&lt;=4\">\n			<brief_description>extraction, 3-4 teeth</brief_description>\n			<gross>8000</gross>\n			<charge>5500</charge>\n		</fee>\n		<fee condition=\"5&lt;=item_no&lt;=9\">\n			<brief_description>extraction, 5-9 teeth</brief_description>\n			<gross>9000</gross>\n			<charge>5500</charge>\n		</fee>\n		<fee condition=\"10&lt;=item_no&lt;=18\">\n			<brief_description>extraction, 10-18 teeth</brief_description>\n			<gross>12000</gross>\n			<charge>5500</charge>\n		</fee>\n		<fee condition=\"item_no&gt;=18\">\n			<brief_description>extraction, &gt; 18 teeth</brief_description>\n			<gross>15000</gross>\n			<charge>5500</charge>\n		</fee>\n	</item>\n	<complex_shortcut>\n		<shortcut att=\"perio\">SP</shortcut>\n		<addition>\n			<case condition=\"n_txs=1\" handled=\"no\"/>\n			<case condition=\"n_txs=2\">\n				<remove_item id=\"E1001\"/>\n				<add_item id=\"E1011\"/>\n				<message>1 visit scale and polish fee removed from estimate. 2 visit scale and polish fee added instead.</message>\n			</case>\n			<case condition=\"n_txs&gt;2\">\n				<alter_item id=\"E1011\"/>\n				<message>maximum fee already claimed for this treatment. Add Privately, or start a new course.</message>\n			</case>\n		</addition>\n		<removal>\n			<case condition=\"n_txs=1\" handled=\"no\"/>\n			<case condition=\"n_txs=2\">\n				<remove_item id=\"E1011\"/>\n				<add_item id=\"E1001\"/>\n				<message>2 visit scale and polish fee removed from estimate, replaced by 1 visit fee.</message>\n			</case>\n			<case condition=\"n_txs&gt;2\">\n				<alter_item id=\"E1011\"/>\n			</case>\n		</removal>\n	</complex_shortcut>\n	<user_display>\n		<crown_chart_button description=\"Porcelain Jacket\" shortcut=\"CR,PJ\" tooltip=\"any tooth\"/>\n		<crown_chart_button description=\"Gold\" shortcut=\"CR,GO\"/>\n		<crown_chart_button description=\"Porcelain/Precious Metal\" shortcut=\"CR,V1\"/>\n		<crown_chart_button description=\"Temporary\" shortcut=\"CR,T1\"/>\n		<crown_chart_button description=\"Resin\" shortcut=\"CR,SR\"/>\n		<crown_chart_button description=\"Lava\" shortcut=\"CR,LAVA\"/>\n		<crown_chart_button description=\"Opalite\" shortcut=\"CR,OPAL\"/>\n		<crown_chart_button description=\"Emax\" shortcut=\"CR,EMAX\"/>\n		<crown_chart_button description=\"Other\" shortcut=\"CR,OT\"/>\n		<crown_chart_button description=\"RECEMENT\" shortcut=\"CR,RC\"/>\n\n		<post_chart_button description=\"Cast Precious Metal\" shortcut=\"CR,C1\" tooltip=\"Lab Made post\"/>\n		<post_chart_button description=\"Cast Non-Precious Metal\" shortcut=\"CR,C2\" tooltip=\"Lab Made post\"/>\n		<post_chart_button description=\"Pre Fabricated Post\" shortcut=\"CR,C3\" tooltip=\"chairside post\"/>\n		<post_chart_button description=\"Other Post\" shortcut=\"CR,OP\"/>\n\n	</user_display>\n</feescale>');
/*!40000 ALTER TABLE `feescales` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feetable_key`
--

DROP TABLE IF EXISTS `feetable_key`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `feetable_key` (
  `ix` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `tablename` char(30) DEFAULT NULL,
  `categories` char(30) DEFAULT NULL,
  `description` char(60) DEFAULT NULL,
  `startdate` date DEFAULT NULL,
  `enddate` date DEFAULT NULL,
  `feecoltypes` tinytext,
  `in_use` tinyint(1) NOT NULL DEFAULT '1',
  `display_order` smallint(6) DEFAULT NULL,
  `data` mediumtext,
  PRIMARY KEY (`ix`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feetable_key`
--

LOCK TABLES `feetable_key` WRITE;
/*!40000 ALTER TABLE `feetable_key` DISABLE KEYS */;
/*!40000 ALTER TABLE `feetable_key` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `formatted_notes`
--

DROP TABLE IF EXISTS `formatted_notes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `formatted_notes` (
  `ix` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `serialno` int(11) DEFAULT NULL,
  `ndate` date DEFAULT NULL,
  `op1` varchar(8) DEFAULT NULL,
  `op2` varchar(8) DEFAULT NULL,
  `ntype` varchar(32) DEFAULT NULL,
  `note` varchar(80) DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `ix` (`ix`),
  KEY `formatted_notes_serialno_index` (`serialno`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `formatted_notes`
--

LOCK TABLES `formatted_notes` WRITE;
/*!40000 ALTER TABLE `formatted_notes` DISABLE KEYS */;
INSERT INTO `formatted_notes` VALUES (1,1,'2014-06-10','REC',NULL,'opened','System date - 10/06/2014 20:26:37','2014-06-10 19:26:37'),(2,1,'2014-06-10','REC',NULL,'newNOTE','This example patient was added to the demo database today.\n','2014-06-10 19:26:37'),(3,1,'2014-06-10','REC',NULL,'closed','REC 10/06/2014 20:26:37','2014-06-10 19:26:37'),(4,1,'2016-09-14','USER',NULL,'opened','System date - 14/09/2016 13:18:01','2016-09-14 12:18:01'),(5,1,'2016-09-14','USER',NULL,'newNOTE','New note added whilst preparing a demo database for release v1.0\n','2016-09-14 12:18:01'),(6,1,'2016-09-14','USER',NULL,'closed','USER 14/09/2016 13:18:01','2016-09-14 12:18:01');
/*!40000 ALTER TABLE `formatted_notes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `forum`
--

DROP TABLE IF EXISTS `forum`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `forum` (
  `ix` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `inits` char(5) DEFAULT NULL,
  `fdate` datetime DEFAULT NULL,
  `topic` char(30) DEFAULT NULL,
  `comment` text NOT NULL,
  `open` tinyint(1) NOT NULL DEFAULT '1',
  `recipient` char(8) DEFAULT NULL,
  PRIMARY KEY (`ix`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forum`
--

LOCK TABLES `forum` WRITE;
/*!40000 ALTER TABLE `forum` DISABLE KEYS */;
INSERT INTO `forum` VALUES (1,'USER','2016-09-14 13:20:13','An Example Message','A forum is useful for inter surgery communication etc.',1,'EVERYBOD'),(2,'USER','2016-09-14 13:20:56','re. An Example Message','thanks.',1,'EVERYBOD'),(3,'USER','2016-09-14 13:22:05','Another Example message','This message has been marked as important by forum user \"USER\"',1,'USER');
/*!40000 ALTER TABLE `forum` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `forum_important`
--

DROP TABLE IF EXISTS `forum_important`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `forum_important` (
  `important_id` int(10) unsigned NOT NULL,
  `op` char(8) DEFAULT NULL,
  KEY `important_id` (`important_id`),
  KEY `forum_important_index` (`op`),
  CONSTRAINT `forum_important_ibfk_1` FOREIGN KEY (`important_id`) REFERENCES `forum` (`ix`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forum_important`
--

LOCK TABLES `forum_important` WRITE;
/*!40000 ALTER TABLE `forum_important` DISABLE KEYS */;
INSERT INTO `forum_important` VALUES (3,'USER');
/*!40000 ALTER TABLE `forum_important` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `forum_parents`
--

DROP TABLE IF EXISTS `forum_parents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `forum_parents` (
  `parent_id` int(10) unsigned NOT NULL,
  `child_id` int(10) unsigned NOT NULL,
  UNIQUE KEY `child_id` (`child_id`,`parent_id`),
  KEY `parent_id` (`parent_id`),
  CONSTRAINT `forum_parents_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `forum` (`ix`),
  CONSTRAINT `forum_parents_ibfk_2` FOREIGN KEY (`child_id`) REFERENCES `forum` (`ix`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forum_parents`
--

LOCK TABLES `forum_parents` WRITE;
/*!40000 ALTER TABLE `forum_parents` DISABLE KEYS */;
INSERT INTO `forum_parents` VALUES (1,2);
/*!40000 ALTER TABLE `forum_parents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `forumread`
--

DROP TABLE IF EXISTS `forumread`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `forumread` (
  `ix` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `id` int(10) unsigned NOT NULL,
  `op` char(8) DEFAULT NULL,
  `readdate` datetime NOT NULL,
  PRIMARY KEY (`ix`),
  KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forumread`
--

LOCK TABLES `forumread` WRITE;
/*!40000 ALTER TABLE `forumread` DISABLE KEYS */;
INSERT INTO `forumread` VALUES (1,1,'USER','2016-09-14 13:20:13'),(2,1,'USER','2016-09-14 13:20:44'),(3,2,'USER','2016-09-14 13:20:56'),(4,3,'USER','2016-09-14 13:22:05'),(5,3,'USER','2016-09-14 13:22:24');
/*!40000 ALTER TABLE `forumread` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medforms`
--

DROP TABLE IF EXISTS `medforms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `medforms` (
  `pt_sno` int(11) unsigned NOT NULL,
  `chk_date` date NOT NULL,
  PRIMARY KEY (`pt_sno`,`chk_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medforms`
--

LOCK TABLES `medforms` WRITE;
/*!40000 ALTER TABLE `medforms` DISABLE KEYS */;
/*!40000 ALTER TABLE `medforms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medhist`
--

DROP TABLE IF EXISTS `medhist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `medhist` (
  `ix` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `pt_sno` int(11) NOT NULL,
  `medication_comments` varchar(200) NOT NULL DEFAULT '',
  `warning_card` varchar(60) NOT NULL DEFAULT '',
  `allergies` varchar(60) NOT NULL DEFAULT '',
  `respiratory` varchar(60) NOT NULL DEFAULT '',
  `heart` varchar(60) NOT NULL DEFAULT '',
  `diabetes` varchar(60) NOT NULL DEFAULT '',
  `arthritis` varchar(60) NOT NULL DEFAULT '',
  `bleeding` varchar(60) NOT NULL DEFAULT '',
  `infectious_disease` varchar(60) NOT NULL DEFAULT '',
  `endocarditis` varchar(60) NOT NULL DEFAULT '',
  `liver` varchar(60) NOT NULL DEFAULT '',
  `anaesthetic` varchar(60) NOT NULL DEFAULT '',
  `joint_replacement` varchar(60) NOT NULL DEFAULT '',
  `heart_surgery` varchar(60) NOT NULL DEFAULT '',
  `brain_surgery` varchar(60) NOT NULL DEFAULT '',
  `hospital` varchar(60) NOT NULL DEFAULT '',
  `cjd` varchar(60) NOT NULL DEFAULT '',
  `other` varchar(60) NOT NULL DEFAULT '',
  `alert` tinyint(1) NOT NULL DEFAULT '0',
  `chkdate` date DEFAULT NULL,
  `modified_by` varchar(20) NOT NULL DEFAULT 'unknown',
  `time_stamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ix`),
  KEY `pt_sno` (`pt_sno`),
  CONSTRAINT `medhist_ibfk_1` FOREIGN KEY (`pt_sno`) REFERENCES `new_patients` (`serialno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medhist`
--

LOCK TABLES `medhist` WRITE;
/*!40000 ALTER TABLE `medhist` DISABLE KEYS */;
/*!40000 ALTER TABLE `medhist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medication_link`
--

DROP TABLE IF EXISTS `medication_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `medication_link` (
  `med_ix` int(11) unsigned NOT NULL,
  `med` varchar(120) DEFAULT NULL,
  `details` varchar(60) DEFAULT NULL,
  KEY `med_ix` (`med_ix`),
  KEY `med` (`med`),
  CONSTRAINT `medication_link_ibfk_1` FOREIGN KEY (`med_ix`) REFERENCES `medhist` (`ix`),
  CONSTRAINT `medication_link_ibfk_2` FOREIGN KEY (`med`) REFERENCES `medications` (`medication`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medication_link`
--

LOCK TABLES `medication_link` WRITE;
/*!40000 ALTER TABLE `medication_link` DISABLE KEYS */;
/*!40000 ALTER TABLE `medication_link` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medications`
--

DROP TABLE IF EXISTS `medications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `medications` (
  `medication` varchar(120) NOT NULL,
  `warning` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`medication`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medications`
--

LOCK TABLES `medications` WRITE;
/*!40000 ALTER TABLE `medications` DISABLE KEYS */;
INSERT INTO `medications` VALUES ('50:50 Ointment',0),('Abacavir Sulphate',0),('Abatacept',0),('Abciximab',0),('Abelcet',0),('Abidec Multivitamin Drops',0),('Abilify',0),('Acamprosate Calcium',0),('Acarbose',0),('Accolate',0),('Accupro',0),('Accuretic',0),('Acea',0),('Acebutolol',0),('Acebutolol Hydrochloride',0),('Aceclofenac',0),('Acemetacin',0),('Acenocoumarol',0),('Acepril',0),('Acetazolamide',0),('Acetic Acid Cough Linctus',0),('Acetylcholine Chloride',0),('Acetylcysteine',0),('Acezide',0),('Aciclovir',0),('Aciclovir Sodium',0),('Acipimox',0),('Acitretin',0),('Aclasta',0),('Acnamino',0),('Acnecide Gel',0),('Acnecide Wash',0),('Acnisal',0),('Acnocin',0),('Acrivastine',0),('Actifed',0),('Actilyse',0),('Activated Charcoal/Magnesium Hydroxide',0),('Actonel',0),('Actonel Combi',0),('Actonorm Gel',0),('Actos',0),('Actrapid',0),('Acular',0),('Acwy Vax',0),('Adalat',0),('Adalimumab',0),('Adapalene',0),('Adartrel',0),('Adcal',0),('Adcal D3',0),('Adcortyl',0),('Adefovir Dipivoxil',0),('Adenocor',0),('Adenosine',0),('Adenuric',0),('Adipine',0),('Adizem',0),('Adrenaline',0),('Adrenaline Acid Tartrate',0),('Advagraf',0),('Aerobec',0),('Afinitor',0),('Aggrastat',0),('Agomelatine',0),('Agrippal',0),('Aknemycin Plus',0),('Aldactide',0),('Aldactone',0),('Aldara',0),('Aldesleukin',0),('Aldioxa/Chloroxylenol',0),('Alemtuzumab',0),('Alendronate Sodium',0),('Alendronate Sodium/Colecalciferol',0),('Alfacalcidol',0),('Alfentanil Hydrochloride',0),('Alfuzosin Hydrochloride',0),('Alimemazine Tartrate',0),('Alimta',0),('Aliskiren',0),('Alitretinoin',0),('Alkeran Injection',0),('Alkeran Tablets',0),('Allantoin/Coal Tar Extract/Hydrocortisone',0),('Allantoin/Lidocaine',0),('Allegron',0),('Allopurinol',0),('Almogran',0),('Almond Oil/Arachis Oil/Camphor',0),('Almotriptan Hydrogen Malate',0),('Alomide',0),('Alphaderm',0),('Alphagan',0),('Alphanine',0),('Alphosyl Hc',0),('Alprazolam',0),('Alprostadil',0),('Altacite Plus',0),('Altargo',0),('Alteplase',0),('Alu-Cap Capsules',0),('Aluminium Hydroxide',0),('Aluminium Sulphate',0),('Alverine',0),('Amantadine Hydrochloride',0),('Amaryl',0),('Ambirix',0),('Ambisome',0),('Ambrisentan',0),('Amias',0),('Amikacin Sulphate',0),('Amikin',0),('Amilamont',0),('Amiloride',0),('Amiloride Hydrochloride',0),('Amiloride/Furosemide',0),('Amiloride/Hydrochlorothiazide',0),('Aminophylline',0),('Amiodarone',0),('Amiodarone Hydrochloride',0),('Amisulpride',0),('Amitriptyline',0),('Amlodipine',0),('Amlodipine Besilate/Valsartan',0),('Amlostin',0),('Ammonia',0),('Ammonia/Eucalyptus',0),('Amorolfine Hydrochloride',0),('Amoxicillin',0),('Amoxil',0),('Amoxil Injection',0),('Amphocil',0),('Amphotericin',0),('Amphotericin Phospholipid Complex',0),('Ampicillin',0),('Ampicillin Sodium/Flucloxacillin Sodium',0),('Amsacrine',0),('Amsidine',0),('Amylase/Lipase/Protease',0),('Anabact',0),('Anacal Rectal Ointment',0),('Anadin Extra Soluble Tablets',0),('Anadin Extra Tablets',0),('Anadin Ibuprofen',0),('Anadin Original',0),('Anadin Paracetamol',0),('Anafranil',0),('Anapen',0),('Anastrozole',0),('Ancotil',0),('Anectine',0),('Anexate',0),('Angeliq',0),('Angettes',0),('Angiox',0),('Angitil',0),('Anidulafungin',0),('Anise Oil/Menthol/Capsicum Tincture',0),('Antabuse',0),('Antazoline/Xylometazoline',0),('Antepsin',0),('Anthisan',0),('Anthisan Bite And Sting Cream',0),('Anugesic-Hc Cream',0),('Anugesic-Hc Suppository',0),('Anusol Cream',0),('Anusol Ointment',0),('Anusol Plus Hc',0),('Anusol Suppositories',0),('Apidra',0),('Apo-Go',0),('Apomorphine Hydrochloride',0),('Apraclonidine Hydrochloride',0),('Aprepitant',0),('Apresoline',0),('Aprinox',0),('Aprovel',0),('Aptivus',0),('Aquadrate',0),('Aranesp',0),('Arava',0),('Arcoxia',0),('Aredia',0),('Argipressin',0),('Aricept',0),('Arimidex',0),('Aripiprazole',0),('Arixtra',0),('Aromasin',0),('Arpicolin',0),('Arsenic Trioxide',0),('Artelac',0),('Artemether/Lumefantrine',0),('Arthrotec',0),('Arythmol',0),('Arzerra',0),('Asacol',0),('Asasantin',0),('Ascorbic Acid/Amylmetacresol/Dichlorobenzyl Alcohol',0),('Ascorbic Acid/Phenylephrine/Paracetamol',0),('Asmabec',0),('Asmanex',0),('Asmasal',0),('Aspirin',0),('Aspirin/Dipyridamole',0),('Aspirin/Paracetamol Dispersible Tablets',0),('Aspro Clear',0),('Atarax',0),('Atazanavir Sulphate',0),('Atenolol',0),('Atenolol/Chlortalidone',0),('Atenolol/Nifedipine',0),('Ativan',0),('Atorvastatin',0),('Atosiban Acetate',0),('Atovaquone/Proguanil Hydrochloride',0),('Atracurium Besilate',0),('Atriance',0),('Atripla',0),('Atropine',0),('Atropine Sulphate',0),('Atrovent',0),('Augmentin',0),('Augmentin Intravenous',0),('Augmentin-Duo',0),('Avamys',0),('Avastin',0),('Avaxim',0),('Avelox',0),('Avloclor',0),('Avodart',0),('Avonex',0),('Axid',0),('Axsain',0),('Azactam',0),('Azathioprine',0),('Azelaic Acid',0),('Azelastine Hydrochloride',0),('Azilect',0),('Azithromycin',0),('Azithromycin Dihydrate',0),('Azopt',0),('Aztreonam',0),('Baby Meltus Cough Linctus',0),('Baclofen',0),('Bactroban',0),('Balneum Bath Oil',0),('Balneum Plus Bath Oil',0),('Balneum Plus Cream',0),('Balsalazide Disodium',0),('Bambec',0),('Bambuterol',0),('Baraclude',0),('Baratol',0),('Basiliximab',0),('Baxan',0),('Bazetham',0),('Bazuka',0),('Bcg (Connaught Strain)',0),('Bcg (Tice Strain)',0),('Beclazone',0),('Beclometasone Dipropionate',0),('Becodisks',0),('Beconase',0),('Bedranol',0),('Beechams',0),('Begrivac',0),('Belimumab',0),('Bemiparin',0),('Bemiparin Sodium',0),('Benadryl',0),('Benadryl Skin Allergy Relief Cream',0),('Bendroflumethiazide',0),('Benefix',0),('Benlysta',0),('Benylin',0),('Benzalkonium Chloride',0),('Benzocaine 1% Spray',0),('Benzoyl Peroxide',0),('Benzydamine Cream',0),('Benzydamine Mouthwash',0),('Benzydamine Oral Spray',0),('Benzylpenicillin Sodium',0),('Beta-Adalat',0),('Beta-Cardone',0),('Beta-Prograne',0),('Betacap',0),('Betadine Dry Powder Spray',0),('Betaferon',0),('Betagan',0),('Betahistine Dihydrochloride',0),('Betaloc',0),('Betamethasone Dipropionate',0),('Betamethasone Valerate',0),('Betaxolol Hydrochloride',0),('Bethanechol Chloride',0),('Betim',0),('Betnovate',0),('Betoptic',0),('Bettamousse',0),('Bevacizumab',0),('Bexarotene',0),('Bezafibrate',0),('Bezalip',0),('Bi-Carzem',0),('Bicalutamide',0),('Bicnu',0),('Bimatoprost',0),('Binovum',0),('Biorphen',0),('Bisacodyl Suppositories',0),('Bisacodyl Tablets',0),('Bismuth Subsalicylate',0),('Bisodol Indigestion Relief Tablets',0),('Bisoprolol Fumarate',0),('Bivalirudin',0),('Bleo-Kyowa',0),('Bleomycin Sulphate',0),('Blistex Relief Cream',0),('Bondronat',0),('Bonefos',0),('Bonjela',0),('Bonviva',0),('Bortezomib',0),('Bosentan',0),('Botox',0),('Brevinor',0),('Brevoxyl Cream',0),('Bricanyl',0),('Bridion',0),('Brilique',0),('Brimonidine Tartrate',0),('Brinzolamide',0),('Brochlor',0),('Broflex',0),('Bromocriptine Mesilate',0),('Brufen',0),('Buccastem',0),('Budesonide',0),('Bumetanide',0),('Bupivacaine Hydrochloride',0),('Bupropion Hydrochloride',0),('Burinex',0),('Burneze Spray',0),('Buscopan',0),('Buserelin Acetate',0),('Busilvex',0),('Buspar',0),('Buspirone',0),('Busulfan',0),('Buttercup Max Strength Sore Throat Lozenge',0),('Buttercup Syrup',0),('Bydureon',0),('Byetta',0),('Cabaser',0),('Cabergoline',0),('Cabren',0),('Cacit',0),('Caelyx',0),('Calaband',0),('Calceos',0),('Calchan',0),('Calcicard',0),('Calcichew',0),('Calcijex',0),('Calcipotriol',0),('Calcitonin (Salmon)',0),('Calcitriol',0),('Calcium Acetate',0),('Calcium Carbonate Antacids',0),('Calcium Carbonate Supplements',0),('Calcium Folinate',0),('Calcium Lactate',0),('Calcium Levofolinate',0),('Calcium Phosphate/Colecalciferol',0),('Calcium-Sandoz Syrup',0),('Calcold Six Plus',0),('Calcort',0),('Calfovit D3',0),('Calmurid Hc',0),('Calpol',0),('Calprofen',0),('Camcolit',0),('Campto',0),('Cancidas',0),('Candesartan',0),('Canesten',0),('Canusal',0),('Capecitabine',0),('Capoten',0),('Capozide',0),('Capreomycin Sulphate',0),('Caprin',0),('Capsaicin',0),('Captopril',0),('Captopril/Hydrochlorothiazide',0),('Carace Plus',0),('Caramet',0),('Carbamazepine',0),('Carbetocin',0),('Carbidopa Monohydrate/Levodopa',0),('Carbidopa/Entacapone/Levodopa',0),('Carbimazole',0),('Carbo-Dome Cream',0),('Carbocisteine',0),('Carbomer',0),('Carbomer Eye Drops',0),('Carboplatin',0),('Carboprost Trometamol',0),('Cardene',0),('Cardicor',0),('Cardioplen',0),('Cardioxane',0),('Cardura',0),('Carmellose Sodium',0),('Carmustine',0),('Casodex',0),('Caspofungin Acetate',0),('Catapres',0),('Caverject',0),('Cayston',0),('Ceanel',0),('Cedocard',0),('Cefaclor Monohydrate',0),('Cefadroxil Monohydrate',0),('Cefalexin',0),('Cefixime',0),('Cefotaxime Sodium',0),('Cefpodoxime Proxetil',0),('Ceftazidime Pentahydrate',0),('Ceftriaxone Sodium',0),('Cefuroxime Axetil',0),('Cefuroxime Sodium',0),('Celance',0),('Celebrex',0),('Celecoxib',0),('Celectol',0),('Celevac Tablets',0),('Celiprolol',0),('Celiprolol Hydrochloride',0),('Cellcept',0),('Cellcept Powder',0),('Celluvisc',0),('Celsentri',0),('Ceplene',0),('Ceporex',0),('Cerazette',0),('Certolizumab Pegol',0),('Cervarix',0),('Cetirizine Liquid',0),('Cetirizine Tablets',0),('Cetraben Bath Additive',0),('Cetraben Emollient Cream',0),('Cetrimide',0),('Cetrimide/Benzalkonium Chloride',0),('Cetrorelix Acetate',0),('Cetrotide',0),('Cetuximab',0),('Cetylpyridinium Chloride Lozenges',0),('Cetylpyridinium Chloride/Menthol',0),('Champix',0),('Chemydur',0),('Chirocaine',0),('Chlorambucil',0),('Chloramphenicol',0),('Chloramphenicol Sodium Succinate',0),('Chlordiazepoxide',0),('Chlordiazepoxide Hydrochloride',0),('Chlorobutanol/Arachis Oil',0),('Chlorobutanol/Lidocaine/Alcloxa/Cetrimide',0),('Chlorocresol/Urea/Cetrimide/Dimeticone',0),('Chloromycetin',0),('Chloroquine',0),('Chloroxylenol',0),('Chlorphenamine Maleate',0),('Chlorpromazine Hydrochloride',0),('Chlortalidone',0),('Cholestagel',0),('Choline Salicylate',0),('Choragon',0),('Choriogonadotropin Alfa',0),('Chorionic Gonadotrophin Human',0),('Cialis',0),('Cibral',0),('Cicafem',0),('Ciclesonide',0),('Ciclosporin',0),('Cidofovir',0),('Cilastatin Sodium/Imipenem Monohydrate',0),('Cilazapril',0),('Cilest',0),('Cilostazol',0),('Cimetidine',0),('Cimzia',0),('Cinacalcet Hydrochloride',0),('Cinchocaine',0),('Cinnarizine',0),('Cipralex',0),('Cipramil',0),('Cipramil Drops',0),('Ciprofibrate',0),('Ciprofloxacin',0),('Ciprofloxacin Hydrochloride',0),('Ciprofloxacin Lactate',0),('Ciproxin Injection',0),('Ciproxin Suspension',0),('Ciproxin Tablets',0),('Circadin',0),('Cisatracurium Besilate',0),('Cisplatin',0),('Citalopram Hydrobromide',0),('Citalopram Hydrochloride',0),('Citanest',0),('Citric Acid/Ipecacuanha',0),('Cladribine',0),('Claforan',0),('Clairette',0),('Clarelux',0),('Clarie Xl',0),('Clarithromycin',0),('Clemastine',0),('Clenil Modulite',0),('Clexane',0),('Climagest',0),('Climaval',0),('Climesse',0),('Clindamycin Hydrochloride',0),('Clindamycin Phosphate',0),('Clioquinol/Flumetasone Pivalate',0),('Clobazam',0),('Clobetasol Propionate',0),('Clobetasone Butyrate',0),('Clofarabine',0),('Clomethiazole',0),('Clomid',0),('Clomifene Citrate',0),('Clomipramine',0),('Clonazepam',0),('Clonidine',0),('Clopamide/Pindolol',0),('Clopidogrel',0),('Clopixol Acuphase',0),('Clopixol Conc',0),('Clopixol Tablets',0),('Clotam',0),('Clotrimazole',0),('Clozapine',0),('Clozaril',0),('Co-Beneldopa',0),('Co-Careldopa',0),('Co-Danthramer',0),('Co-Diovan',0),('Co-Fluampicil',0),('Co-Magaldrox',0),('Co-Simalcite',0),('Co-Trimoxazole',0),('Co-Zidocapt',0),('Coaprovel',0),('Cobalin-H',0),('Codeine/Paracetamol',0),('Colazide',0),('Colchicine',0),('Colecalciferol/Calcium Carbonate',0),('Colesevelam Hydrochloride',0),('Colestid',0),('Colestipol',0),('Colestipol Hydrochloride',0),('Colestyramine Anhydrous',0),('Colifoam',0),('Colistimethate Sodium',0),('Colistin Sulphate',0),('Colofac',0),('Colomycin',0),('Colomycin Injection',0),('Colomycin Syrup',0),('Colomycin Tablet',0),('Colpermin Ibs Relief Capsules',0),('Combigan',0),('Combivent',0),('Combivir',0),('Combodart',0),('Competact',0),('Compound W',0),('Comtess',0),('Concerta Xl',0),('Condyline',0),('Conjugated Oestrogens',0),('Copaxone',0),('Copegus',0),('Coracten',0),('Cordarone X',0),('Cordilox',0),('Corgard',0),('Corifollitropin Alfa',0),('Cortisone Acetate',0),('Cosmofer',0),('Cosopt',0),('Coversyl Arginine',0),('Coversyl Arginine Plus',0),('Cozaar',0),('Cozaar-Comp',0),('Cream Of Magnesia Tablets',0),('Creon',0),('Crestor',0),('Crinone',0),('Cromogen',0),('Crotamiton',0),('Cubicin',0),('Cuprofen',0),('Cuprofen Plus',0),('Cutivate',0),('Cyanocobalamin',0),('Cyclizine Lactate',0),('Cyclo-Progynova 2Mg',0),('Cyclopentolate Hydrochloride',0),('Cyclophosphamide Monohydrate',0),('Cycloserine',0),('Cyklokapron',0),('Cymalon',0),('Cymbalta',0),('Cymevene',0),('Cymex Cream',0),('Cyproheptadine',0),('Cyprostat',0),('Cyproterone Acetate',0),('Cyproterone Acetate/Ethinylestradiol',0),('Cystrin',0),('Cytamen',0),('Cytarabine',0),('Cytotec',0),('D-Gam',0),('Dabigatran Etexilate Mesilate',0),('Dacarbazine Citrate',0),('Daktacort',0),('Daktarin Oral Gel',0),('Dalacin',0),('Dalacin C',0),('Dalmane',0),('Dalteparin',0),('Danaparoid',0),('Danazol',0),('Dandrazol',0),('Danol',0),('Dantrium',0),('Dantrolene Sodium',0),('Daptomycin',0),('Daraprim',0),('Darbepoetin Alfa',0),('Darifenacin Hydrobromide',0),('Darunavir Ethanolate',0),('Dasatinib',0),('Daunorubicin Hydrochloride Citrate',0),('Daunoxome',0),('Daxas',0),('Day Nurse',0),('Day Nurse Capsules',0),('Ddavp',0),('Deca-Durabolin',0),('Decapeptyl',0),('Defanac',0),('Deferasirox',0),('Deferiprone',0),('Deflazacort',0),('Deltacortril',0),('Deltastab',0),('Demeclocycline Hydrochloride',0),('Denosumab',0),('Denzapine',0),('Depakote',0),('Depixol',0),('Depixol Tablets',0),('Depo-Medrone',0),('Depo-Medrone With Lidocaine',0),('Depo-Provera',0),('Depocyte',0),('Dequacaine',0),('Dequadin',0),('Dequalinium',0),('Derbac M',0),('Dermalo Bath Emollient',0),('Dermamist',0),('Dermax',0),('Dermidex',0),('Dermovate',0),('Deseril',0),('Desferal',0),('Desferrioxamine Mesilate',0),('Desloratadine',0),('Desmomelt',0),('Desmopressin Acetate',0),('Desmospray',0),('Desmotabs',0),('Desogestrel',0),('Destolit',0),('Detrunorm',0),('Detrusitol',0),('Dexamethasone',0),('Dexibuprofen',0),('Dexketoprofen Trometamol',0),('Dexomon',0),('Dexrazoxane',0),('Dexsol',0),('Dextromethorphan',0),('Dextromethorphan/Menthol',0),('Dextromethorphan/Pseudoephedrine',0),('Dhc Continus',0),('Diamicron',0),('Diamorphine',0),('Diamox',0),('Dianette',0),('Diazemuls',0),('Diazepam',0),('Dichlorobenzyl Alcohol/Amylmetacresol',0),('Diclofenac Diethylammonium',0),('Diclofenac Epolamine',0),('Diclofenac Potassium',0),('Diclofenac Sodium',0),('Diclofenac Sodium/Misoprostol',0),('Dicloflex',0),('Diclomax',0),('Dicycloverine Hydrochloride',0),('Dicynene',0),('Didanosine',0),('Didronel',0),('Didronel Pmo',0),('Diethylamine Salicylate',0),('Differin',0),('Difflam Cream',0),('Difflam Solution',0),('Difflam Spray',0),('Diflucan',0),('Digoxin',0),('Dihydrocodeine Tartrate',0),('Dilcardia',0),('Dill Oil/Sodium Bicarbonate/Ginger',0),('Diloxanide Furoate',0),('Diltiazem',0),('Diltiazem Hydrochloride',0),('Dilzem',0),('Dimeticone',0),('Dinoprostone',0),('Diocalm',0),('Dioctyl',0),('Dioderm',0),('Dioralyte',0),('Dioralyte Relief',0),('Diovan',0),('Dipentum',0),('Diphenhydramine',0),('Dipivefrine Hydrochloride',0),('Diprivan',0),('Diprobase Cream',0),('Diprobase Ointment',0),('Diprobath',0),('Diprosalic',0),('Diprosone',0),('Dipyridamole',0),('Disipal',0),('Disodium Etidronate',0),('Disodium Folinate',0),('Disodium Pamidronate',0),('Disopyramide',0),('Disopyramide Phosphate',0),('Disprin',0),('Disprin Extra',0),('Distaclor',0),('Distamine',0),('Distigmine Bromide',0),('Distilled Witch Hazel',0),('Disulfiram',0),('Dithranol',0),('Dithrocream',0),('Ditropan',0),('Diurexan',0),('Dixarit',0),('Do-Do Chesteze',0),('Dobutamine Hydrochloride',0),('Docetaxel',0),('Docusate',0),('Docusate Gel Enema',0),('Docusate Sodium Ear Drops',0),('Dolmatil',0),('Domperidone',0),('Domperidone Maleate',0),('Dopamine',0),('Dopamine Hydrochloride',0),('Dopexamine',0),('Doralese Tiltab',0),('Doribax',0),('Doripenem Monohydrate',0),('Dornase Alfa',0),('Dorzolamide Hydrochloride',0),('Dorzolamide Hydrochloride/Timolol Maleate',0),('Doublebase Bath Additive',0),('Doublebase Gel',0),('Doublebase Shower Gel',0),('Doublebase Wash Gel',0),('Dovobet',0),('Dovonex',0),('Dovonex Cream',0),('Doxadura',0),('Doxazosin',0),('Doxazosin Mesilate',0),('Doxorubicin Hydrochloride',0),('Doxorubin',0),('Doxycycline Hyclate',0),('Doxycycline Monohydrate',0),('Doxylamine/Pseudoephedrine/Dextromethorphan/Paracetamol',0),('Doxylar',0),('Dozic',0),('Drapolene Cream',0),('Dromadol',0),('Dronedarone Hydrochloride',0),('Drospirenone/Estradiol Hemihydrate',0),('Drospirenone/Ethinylestradiol',0),('Drotrecogin Alfa',0),('Droxia',0),('Duac',0),('Dukoral',0),('Dulcobalance',0),('Dulcoease',0),('Dulcolax Suppositories',0),('Dulcolax Tablets',0),('Duloxetine',0),('Duloxetine Hydrochloride',0),('Duodopa',0),('Duofilm',0),('Duotrav',0),('Duovent',0),('Dutasteride',0),('Dydrogesterone/Estradiol',0),('Dysport',0),('E45 Cream',0),('E45 Itch Relief Cream',0),('Earex Ear Drops',0),('Earex Plus',0),('Easyhaler Beclometasone',0),('Easyhaler Budesonide',0),('Easyhaler Formoterol',0),('Easyhaler Salbutamol',0),('Ebixa',0),('Ecalta',0),('Eccoxolac',0),('Econac',0),('Econazole Nitrate',0),('Ecopace',0),('Eczmol',0),('Edronax',0),('Edrophonium Chloride',0),('Efavirenz',0),('Efcortesol',0),('Efexor',0),('Efient',0),('Eflornithine Monohydrate Chloride',0),('Efudix',0),('Eldepryl',0),('Electrolade',0),('Eletriptan Hydrobromide',0),('Elidel',0),('Ellaone',0),('Elleste Solo',0),('Ellimans Universal Muscle Rub Lotion',0),('Elocon',0),('Elonva',0),('Eloxatin',0),('Eludril Mouthwash',0),('Eludril Spray',0),('Emadine',0),('Emcor',0),('Emedastine Difumarate',0),('Emend',0),('Emeside',0),('Emflex',0),('Emla',0),('Emselex',0),('Emtricitabine',0),('Emtricitabine/Tenofovir Disoproxil Fumarate',0),('Emtriva',0),('Emulsiderm Emollient',0),('Enalapril',0),('Enalapril/Hydrochlorothiazide',0),('Enbrel',0),('Endoxana',0),('Enfuvirtide',0),('Engerix B',0),('Eno',0),('Enoxaparin',0),('Enoxaparin Sodium',0),('Entacapone',0),('Entecavir Monohydrate',0),('Entocort',0),('Enzira',0),('Epanutin Capsules',0),('Epanutin Infatabs',0),('Epanutin Ready Mixed Parenteral',0),('Epanutin Suspension',0),('Epaxal',0),('Ephedrine Hydrochloride',0),('Ephedrine Hydrochloride/Chlorphenamine',0),('Ephedrine Nasal Drops',0),('Epilim',0),('Epinastine Hydrochloride',0),('Epipen',0),('Epirubicin Hydrochloride',0),('Epival',0),('Epivir',0),('Eplerenone',0),('Epoetin Alfa',0),('Epoetin Beta',0),('Epoprostenol',0),('Eposin',0),('Eprex',0),('Eprosartan',0),('Eprosartan Mesilate',0),('Epsom Salts',0),('Eptacog Alfa',0),('Eptifibatide',0),('Erbitux',0),('Erdosteine',0),('Erdotin',0),('Ergometrine Maleate',0),('Ergometrine Maleate/Oxytocin',0),('Erlotinib Hydrochloride',0),('Ertapenem Sodium',0),('Eryacne 4',0),('Erymax',0),('Erythrocin',0),('Erythromycin',0),('Erythromycin Ethyl Succinate',0),('Erythromycin Lactobionate',0),('Erythromycin Stearate',0),('Erythromycin/Isotretinoin',0),('Erythromycin/Tretinoin',0),('Erythromycin/Zinc Acetate',0),('Erythroped',0),('Escitalopram',0),('Escitalopram Oxalate',0),('Esmeron',0),('Esmya',0),('Esomeprazole Injection',0),('Esomeprazole Tablets',0),('Estracyt',0),('Estraderm',0),('Estradiol',0),('Estradiol Hemihydrate',0),('Estradiol Hemihydrate/Norethisterone Acetate',0),('Estradiol Valerate',0),('Estradiol Valerate/Medroxyprogesterone',0),('Estradiol Valerate/Medroxyprogesterone Acetate',0),('Estradiol Valerate/Norethisterone',0),('Estradiol Valerate/Norgestrel',0),('Estradiol/Estriol/Estrone',0),('Estradiol/Levonorgestrel',0),('Estradiol/Norethisterone Acetate',0),('Estradot',0),('Estramustine Sodium Phosphate',0),('Estring',0),('Estriol',0),('Estropipate',0),('Etamsylate',0),('Etanercept',0),('Ethanolamine',0),('Ethinylestradiol',0),('Ethinylestradiol/Etonogestrel',0),('Ethinylestradiol/Gestodene',0),('Ethinylestradiol/Levonorgestrel',0),('Ethinylestradiol/Norelgestromin',0),('Ethinylestradiol/Norethisterone',0),('Ethinylestradiol/Norethisterone Acetate',0),('Ethinylestradiol/Norgestimate',0),('Ethosuximide',0),('Etodolac',0),('Etomidate',0),('Etonogestrel',0),('Etopophos',0),('Etoposide',0),('Etoposide Phosphate',0),('Etoricoxib',0),('Etravirine',0),('Etynodiol Diacetate',0),('Eucalyptus/Menthol/Cetylpyridinium Chloride',0),('Eucalyptus/Terpineol/Methyl Salicylate/Menthol/Camphor',0),('Eucalyptus/Thyme/Menthol',0),('Eucalyptus/Turpentine/Levomenthol/Camphor',0),('Eucalyptus/Turpentine/Methyl Salicylate/Menthol',0),('Eucreas',0),('Eumocream',0),('Eumovate',0),('Eurax',0),('Eurax Hydrocortisone',0),('Everolimus',0),('Evista',0),('Evoltra',0),('Evorel',0),('Evorel Conti',0),('Evorel Sequi',0),('Evra',0),('Ex-Lax Senna',0),('Exelon',0),('Exelon Patches',0),('Exemestane',0),('Exenatide',0),('Exforge',0),('Exjade',0),('Exocin',0),('Exorex Lotion',0),('Extavia',0),('Exterol',0),('Ezetimibe',0),('Ezetimibe/Simvastatin',0),('Ezetrol',0),('Factor Ii/Factor Vii/Protein S/Factor X/Protein C/Factor Ix',0),('Factor Ix High Purity',0),('Factor Viii/Von Willebrand Factor',0),('Factor Xiii',0),('Famciclovir',0),('Family Meltus Chesty Coughs',0),('Famotidine',0),('Famotidine/Calcium Carbonate/Magnesium Hydroxide',0),('Famvir',0),('Fareston',0),('Fasigyn',0),('Faslodex',0),('Faverin',0),('Febuxostat',0),('Felbinac',0),('Feldene',0),('Felendil',0),('Felodipine',0),('Felodipine/Ramipril',0),('Felogen',0),('Felotens',0),('Femapak',0),('Femara',0),('Fematrix',0),('Femodene',0),('Femodette',0),('Femoston',0),('Femseven Conti',0),('Femseven Patches',0),('Femseven Sequi',0),('Femulen',0),('Fenactol',0),('Fendrix',0),('Fenistil',0),('Fenofibrate',0),('Fenofibrate Micronised',0),('Fenoterol/Ipratropium',0),('Fenticonazole Nitrate',0),('Ferinject',0),('Ferric Carboxymaltose',0),('Ferriprox',0),('Ferrous Fumarate',0),('Ferrous Fumarate/Folic Acid',0),('Ferrous Sulphate Tablets',0),('Ferrous Sulphate/Ascorbic Acid',0),('Fersaday',0),('Fersamal',0),('Fesoterodine Fumarate',0),('Fexofenadine Hydrochloride',0),('Fibrazate',0),('Fibro-Vein',0),('Fibrogammin P',0),('Filgrastim',0),('Finacea',0),('Finasteride',0),('Fingolimod Hydrochloride',0),('Flagyl',0),('Flagyl-S',0),('Flamatak',0),('Flamrase',0),('Flavoxate Hydrochloride',0),('Flecainide',0),('Flecainide Acetate',0),('Flexin',0),('Flixonase',0),('Flixonase Allergy',0),('Flixotide',0),('Flolan',0),('Flomaxtra',0),('Florinef',0),('Floxapen',0),('Fluanxol',0),('Fluarix',0),('Flucloxacillin Sodium',0),('Fluconazole',0),('Fluconazole And Clotrimazole',0),('Flucytosine',0),('Fludara',0),('Fludarabine Phosphate',0),('Fludrocortisone Acetate',0),('Fluimucil N',0),('Flumazenil',0),('Fluorescein Sodium/Lidocaine Hydrochloride',0),('Fluorescein Sodium/Proxymetacaine Hydrochloride',0),('Fluorometholone',0),('Fluorouracil',0),('Fluorouracil Sodium',0),('Fluoxetine',0),('Flupentixol',0),('Flupentixol Decanoate',0),('Flupentixol Dihydrochloride',0),('Fluphenazine Decanoate',0),('Flurazepam',0),('Flurazepam Hydrochloride',0),('Flurbiprofen',0),('Flurbiprofen Sodium',0),('Fluticasone Furoate',0),('Fluticasone Propionate',0),('Fluticasone/Salmeterol',0),('Fluvastatin',0),('Fluvastatin Sodium',0),('Fluvirin',0),('Fluvoxamine',0),('Fluvoxamine Maleate',0),('Fml',0),('Folic Acid',0),('Follitropin Alfa',0),('Follitropin Alfa/Lutropin Alfa',0),('Follitropin Beta',0),('Fondaparinux',0),('Foradil',0),('Forceval',0),('Formaldehyde',0),('Formoterol Fumarate Dihydrate',0),('Forsteo',0),('Fortipine',0),('Fortum',0),('Fosamax',0),('Fosamprenavir Calcium',0),('Fosavance',0),('Foscarnet Sodium',0),('Foscavir',0),('Fosinopril',0),('Fosphenytoin Sodium',0),('Fosrenol',0),('Fostair',0),('Fragmin',0),('Freederm Gel',0),('Frisium',0),('Froben',0),('Frovatriptan Succinate Monohydrate',0),('Fru-Co',0),('Frumil',0),('Frusene',0),('Frusol',0),('Fucibet',0),('Fucidin Cream',0),('Fucidin H',0),('Fucidin H Ointment',0),('Fucidin Ointment',0),('Fucidin Suspension',0),('Fucidin Tablets',0),('Fucithalmic',0),('Fulvestrant',0),('Fungizone',0),('Furadantin',0),('Furosemide',0),('Furosemide/Spironolactone',0),('Furosemide/Triamterene',0),('Fusidic Acid',0),('Fusidic Acid/Hydrocortisone Acetate',0),('Fuzeon',0),('Fybogel',0),('Fybogel Mebeverine',0),('Gabapentin',0),('Gabitril',0),('Gadobutrol',0),('Gadoteridol',0),('Gadovist',0),('Gadoxetate Disodium',0),('Galantamine Hydrobromide',0),('Galvus',0),('Gamanil',0),('Ganciclovir Sodium',0),('Ganfort',0),('Ganirelix',0),('Gardasil',0),('Garlic Oil/Garlic/Echinacea',0),('Gastrobid',0),('Gastrocote Liquid',0),('Gastrocote Tablets',0),('Gaviscon Advance',0),('Gaviscon Cool Tablets',0),('Gaviscon Double Action',0),('Gaviscon Extra Strength Tablets',0),('Gaviscon Infant Oral Powder',0),('Gaviscon Liquid Sachets',0),('Gaviscon Tablets',0),('Gefitinib',0),('Geltears',0),('Gemcitabine Hydrochloride',0),('Gemeprost',0),('Gemfibrozil',0),('Gemzar',0),('Generic Abidec Multivitamin Drops',0),('Generic Actonorm Powder',0),('Generic Alginate/Aluminium Hydroxide/Magnesium Carbonate',0),('Generic Antitis Tablets',0),('Generic Calcimax Liquid',0),('Generic Catarrh Relief Mixture',0),('Generic Cetanorm Cream',0),('Generic Chest Mixture',0),('Generic Cymalon Granules',0),('Generic Dalivit Oral Drops',0),('Generic Deep Heat Spray',0),('Generic Diocalm',0),('Generic Dioralyte Powder',0),('Generic Dioralyte Relief',0),('Generic Diprobase Cream',0),('Generic Dubam Cream',0),('Generic Dulbalm Cream',0),('Generic Electrolade Powder',0),('Generic Fiery Jack Cream',0),('Generic Forceval Capsules',0),('Generic Germolene Antiseptic Ointment',0),('Generic Glycerin, Honey And Lemon Linctus',0),('Generic Indian Brandee',0),('Generic Karvol Decongestant Capsules',0),('Generic Karvol Decongestant Drops',0),('Generic Ketovite Liquid',0),('Generic Laxido',0),('Generic Lipobase',0),('Generic Metanium Barrier Ointment',0),('Generic Meted Shampoo',0),('Generic Molaxole Powder',0),('Generic Oxymetazoline',0),('Generic Pharmaton Vitality Capsules',0),('Generic Phytex',0),('Generic Polytar Af Liquid',0),('Generic Polytar Emollient',0),('Generic Polytar Liquid',0),('Generic Polytar Plus Liquid',0),('Generic Potter\'S Strong Bronchial Catarrh Pastilles',0),('Generic Potter\'S Sugar Free Cough Pastilles',0),('Generic Radian B Muscle Lotion',0),('Generic Rehydration Powder',0),('Generic Resolve Effervescent Granules',0),('Generic Sciargo Tablets',0),('Generic Senokot Comfort Tablets',0),('Generic Senokot Dual Relief Tablets',0),('Generic Sudocrem Cream',0),('Generic Tcp Antiseptic Cream',0),('Generic Tcp Antiseptic Ointment',0),('Generic Throaties Strong Original Pastilles',0),('Generic Transvasin Spray',0),('Generic Ultrabase',0),('Generic Unguentum M Cream',0),('Generic Vadarex Ointment',0),('Generic Vegetable Cough Remover Elixir',0),('Genotropin',0),('Gentamicin Sulphate',0),('Gentamicin Sulphate/Hydrocortisone Acetate',0),('Gentisone',0),('Germolene Antiseptic Cream',0),('Germolene Antiseptic First Aid Wash',0),('Germolene Antiseptic Ointment',0),('Germoloids Cream',0),('Germoloids Duo Pack',0),('Germoloids Hc Spray',0),('Germoloids Ointment',0),('Germoloids Suppositories',0),('Gestone',0),('Gestrinone',0),('Gilenya',0),('Glatiramer Acetate',0),('Gliadel',0),('Glibenese',0),('Gliclazide',0),('Glimepiride',0),('Glipizide',0),('Glivec',0),('Glucagen',0),('Glucagon',0),('Glucobay',0),('Glucophage',0),('Glucose Anhydrous',0),('Glucose/Treacle Cough Mixture',0),('Glutaraldehyde',0),('Glutarol',0),('Glycerin And Blackcurrant Cough Syrup',0),('Glycerin, Honey And Lemon Linctus',0),('Glycerin, Honey, Lemon And Ipecacuanha Linctus',0),('Glycerol Cream',0),('Glycerol Oral Solution',0),('Glycerol Skin Wash',0),('Glycerol/Glucose Cough Mixture',0),('Glycerol/Sucrose Cough Mixture',0),('Glycerol/Syrup/Citric Acid/Honey/Lemon',0),('Glycerol/White Soft Paraffin/Liquid Paraffin',0),('Glyceryl Trinitrate',0),('Glycopyrronium Bromide',0),('Goddards Muscle Lotion',0),('Golimumab',0),('Gonapeptyl',0),('Gopten',0),('Goserelin Acetate',0),('Granisetron Hydrochloride',0),('Granocyte-13',0),('Grass Pollen Extract',0),('Grazax',0),('Griseofulvin',0),('Grisol Af',0),('Guaiacol/Codeine',0),('Guaifenesin',0),('Guaifenesin/Ammonium Chloride/Ammonium Carbonate',0),('Guaifenesin/Cetylpyridinium Chloride',0),('Guaifenesin/Levomenthol',0),('Guaifenesin/Pseudoephedrine',0),('Guaifenesin/Treacle/Glucose',0),('Guanethidine',0),('Guanethidine Monosulphate',0),('Gygel',0),('Gyno-Daktarin',0),('Gyno-Pevaryl',0),('Gynoxin',0),('Haemate P',0),('Haemorrhoid Relief Ointment',0),('Haldol',0),('Haldol Decanoate',0),('Halogenated Phenols/Phenol',0),('Haloperidol',0),('Haloperidol Decanoate',0),('Hamol Senna Tablets',0),('Happinose',0),('Harmogen',0),('Havrix',0),('Haymine Tablets',0),('Hbvaxpro',0),('Hedex',0),('Hedex Extra',0),('Hedex Ibuprofen',0),('Helixate Nexgen',0),('Hemabate',0),('Heminevrin Capsules',0),('Heparin Sodium',0),('Hepatyrix',0),('Hepsal',0),('Hepsera',0),('Herceptin',0),('Herpid',0),('Hexetidine',0),('Hexopal',0),('Hexylresorcinol',0),('Hexylresorcinol/Benzalkonium Chloride',0),('Hiprex',0),('Histac',0),('Histamine Dihydrochloride',0),('Honey/Glucose/Lemon',0),('Honey/Menthol',0),('Horizem',0),('Hormonin',0),('Humalog',0),('Humalog Mix',0),('Humatrope',0),('Humira',0),('Humulin I',0),('Humulin M3',0),('Humulin S',0),('Hyaluronidase',0),('Hycamtin',0),('Hydralazine',0),('Hydralazine Hydrochloride',0),('Hydrea',0),('Hydrochlorothiazide/Irbesartan',0),('Hydrochlorothiazide/Losartan',0),('Hydrochlorothiazide/Olmesartan',0),('Hydrochlorothiazide/Olmesartan Medoxomil',0),('Hydrochlorothiazide/Quinapril',0),('Hydrochlorothiazide/Telmisartan',0),('Hydrochlorothiazide/Valsartan',0),('Hydrocortisone',0),('Hydrocortisone Acetate',0),('Hydrocortisone Acetate/Lidocaine',0),('Hydrocortisone Acetate/Pramocaine Hydrochloride',0),('Hydrocortisone Acetate/Sodium Fusidate',0),('Hydrocortisone Butyrate',0),('Hydrocortisone Sodium Phosphate',0),('Hydrocortisone Sodium Succinate',0),('Hydrocortisone/Lactic Acid/Urea',0),('Hydrocortisone/Lidocaine',0),('Hydrocortisone/Miconazole Nitrate',0),('Hydrocortisone/Neomycin Sulphate/Polymyxin B Sulphate',0),('Hydrocortisone/Urea',0),('Hydrocortistab',0),('Hydroflumethiazide/Spironolactone',0),('Hydromol Bath And Shower Emollient',0),('Hydromol Cream',0),('Hydrotalcite Suspension',0),('Hydroxocobalamin',0),('Hydroxycarbamide',0),('Hydroxychloroquine',0),('Hydroxychloroquine Sulphate',0),('Hydroxyethyl Salicylate/Methyl Nicotinate',0),('Hydroxyethyl Salicylate/Methyl Nicotinate/Capsicum Oleoresin',0),('Hydroxyzine Hydrochloride',0),('Hyetellose',0),('Hygroton',0),('Hyoscine',0),('Hyoscine Butylbromide',0),('Hyoscine Hydrobromide',0),('Hypnomidate',0),('Hypnovel',0),('Hypolar',0),('Hypovase',0),('Hypromellose',0),('Hypromellose/Dextran 70',0),('Hypurin Bovine Isophane',0),('Hypurin Bovine Lente',0),('Hypurin Bovine Neutral',0),('Hypurin Bovine Protamine Zinc',0),('Hypurin Porcine',0),('Hypurin Porcine Isophane',0),('Hypurin Porcine Neutral',0),('Hytrin',0),('Ibandronic Sodium Monohydrate',0),('Ibufem',0),('Ibuprofen',0),('Ibuprofen/Codeine Phosphate',0),('Ibuprofen/Levomenthol',0),('Ibuprofen/Phenylephrine',0),('Ibuprofen/Pseudoephedrine',0),('Idarubicin Hydrochloride',0),('Idoxuridine',0),('Iglu Gel',0),('Ikorel',0),('Iloprost Trometamol',0),('Ilube',0),('Imatinib Mesilate',0),('Imigran',0),('Imigran Nasal Spray',0),('Imigran Recovery',0),('Imipramine Hydrochloride',0),('Imiquimod',0),('Immucyst',0),('Imodium',0),('Imodium Plus',0),('Implanon',0),('Imunovir',0),('Imuran',0),('Imuvac',0),('Incivo',0),('Increlex',0),('Indacaterol Maleate',0),('Indapamide',0),('Indapamide Hemihydrate',0),('Indapamide/Perindopril Arginine',0),('Inderal',0),('Indivina',0),('Indolar',0),('Indometacin',0),('Indomod',0),('Indoramin Hydrochloride',0),('Inegy',0),('Infacol',0),('Infanrix Ipv',0),('Infanrix-Ipv+Hib',0),('Infliximab',0),('Influenza Vaccine',0),('Influvac',0),('Innohep',0),('Innovace',0),('Innozide',0),('Inosine Pranobex',0),('Inositol Nicotinate',0),('Inovelon',0),('Inspra',0),('Insulatard',0),('Insulin Aspart',0),('Insulin Aspart/Insulin Aspart Protamine',0),('Insulin Detemir',0),('Insulin Glargine',0),('Insulin Glulisine',0),('Insulin Isophane Bovine',0),('Insulin Isophane Human',0),('Insulin Isophane Human/Insulin Soluble Human',0),('Insulin Isophane Porcine',0),('Insulin Isophane Porcine/Insulin Soluble Porcine',0),('Insulin Lispro',0),('Insulin Lispro/Insulin Lispro Protamine',0),('Insulin Protamine Zinc Bovine',0),('Insulin Soluble Bovine',0),('Insulin Soluble Human',0),('Insulin Soluble Porcine',0),('Insulin Zinc Suspension Mixed Bovine',0),('Insuman Basal',0),('Insuman Comb',0),('Insuman Rapid',0),('Intal',0),('Integrilin',0),('Intelence',0),('Interferon Alfa-2A (Rbe)',0),('Interferon Alfa-2B (Rbe)',0),('Interferon Beta-1A',0),('Interferon Beta-1B',0),('Introna',0),('Invanz',0),('Invega',0),('Invirase',0),('Iopidine',0),('Ipocol',0),('Ipratropium',0),('Ipratropium/Salbutamol',0),('Irbesartan',0),('Iressa',0),('Irinotecan Hydrochloride Trihydrate',0),('Iron Dextran',0),('Iron Sucrose',0),('Isentress',0),('Ismelin',0),('Isocarboxazid',0),('Isoflurane',0),('Isoket',0),('Isoniazid',0),('Isoniazid/Pyrazinamide/Rifampicin',0),('Isoniazid/Rifampicin',0),('Isopropyl Myristate/Liquid Paraffin',0),('Isopto Alkaline',0),('Isopto Plain',0),('Isosorbide Dinitrate',0),('Isosorbide Mononitrate',0),('Isotretinoin',0),('Isotrex',0),('Isotrexin',0),('Isovorin',0),('Ispaghula Husk Granules',0),('Ispaghula Husk/Mebeverine',0),('Isradipine',0),('Istin',0),('Itraconazole',0),('Ivabradine',0),('Ixiaro',0),('Janumet',0),('Januvia',0),('Javlor',0),('Junior Meltus Chesty Coughs With Catarrh',0),('Kaletra',0),('Kaolin And Morphine Mixture',0),('Kaolin/Calcium Carbonate',0),('Karvol Decongestant Capsules',0),('Karvol Decongestant Drops',0),('Kefadim',0),('Keflex',0),('Keftid',0),('Kemadrin',0),('Kemicetine',0),('Kenalog',0),('Kentera',0),('Kentipine',0),('Kenzem',0),('Keppra',0),('Keral',0),('Ketalar',0),('Ketamine Hydrochloride',0),('Ketek',0),('Ketocid',0),('Ketoconazole',0),('Ketoprofen',0),('Ketorolac Trometamol',0),('Ketotifen',0),('Ketovail',0),('Ketovite Liquid',0),('Kivexa',0),('Klaricid',0),('Kliofem',0),('Kliovance',0),('Kolanticon Gel',0),('Kytril',0),('Lacidipine',0),('Lacosamide',0),('Lacrilube',0),('Lactulose',0),('Lamictal',0),('Lamisil',0),('Lamivudine',0),('Lamivudine/Zidovudine',0),('Lamotrigine',0),('Lanacane Cream',0),('Lanolin/White Soft Paraffin/Liquid Paraffin',0),('Lanoxin',0),('Lanreotide Acetate',0),('Lansoprazole',0),('Lanthanum Carbonate',0),('Lantus',0),('Lanvis',0),('Lapatinib Ditosylate Monohydrate',0),('Larapam',0),('Largactil',0),('Lariam',0),('Laryng-O-Jet',0),('Lasilactone',0),('Lasix',0),('Lasoride',0),('Latanoprost',0),('Latanoprost/Timolol Maleate',0),('Lauromacrogol 400/Heparinoid',0),('Laxido',0),('Leflunomide',0),('Lemon/Honey/Levomenthol/Citric Acid',0),('Lemsip Cold And Flu',0),('Lemsip Cough Chesty',0),('Lemsip Dry Cough Liquid',0),('Lemsip Flu 12 Hour Ibuprofen And Pseudoephedrine',0),('Lemsip Max All Day Cold And Flu Tablets',0),('Lemsip Max All Night Cold And Flu Tablets',0),('Lemsip Max All-In-One',0),('Lemsip Max Cold And Flu Breathe Easy',0),('Lemsip Max Cold And Flu Direct',0),('Lemsip Max Day And Night Cold And Flu Relief Capsules',0),('Lemsip Max Flu',0),('Lemsip Max Sinus',0),('Lemsip Max Sinus Capsules',0),('Lenalidomide',0),('Lenograstim (Rch)',0),('Lercanidipine',0),('Lescol',0),('Letrozole',0),('Leukeran',0),('Leuprorelin Acetate',0),('Leustat',0),('Levemir',0),('Levetiracetam',0),('Levitra',0),('Levobunolol Hydrochloride',0),('Levobupivacaine Hydrochloride',0),('Levocetirizine Dihydrochloride',0),('Levofloxacin',0),('Levofloxacin Hemihydrate',0),('Levomenthol',0),('Levomenthol/Amylmetacresol/Dichlorobenzyl Alcohol',0),('Levomenthol/Squill/Liquorice',0),('Levomepromazine Maleate',0),('Levonelle',0),('Levonorgestrel',0),('Levothyroxine Sodium',0),('Lexpec Folic Acid',0),('Li-Liquid',0),('Librium',0),('Librofem',0),('Lidocaine',0),('Lidocaine Hydrochloride',0),('Lidocaine Hydrochloride/Adrenaline Acid Tartrate',0),('Lidocaine/Aminoacridine',0),('Lidocaine/Cetalkonium Chloride',0),('Lidocaine/Cetylpyridinium Chloride',0),('Lidocaine/Chlorhexidine',0),('Lidocaine/Chlorocresol/Cetylpyridinium Chloride',0),('Lidocaine/Methylprednisolone Acetate',0),('Lidocaine/Zinc Sulphate/Cetrimide',0),('Light Liquid Paraffin',0),('Linezolid',0),('Lioresal',0),('Liothyronine Sodium',0),('Lipantil',0),('Lipitor',0),('Lipobase',0),('Liposic',0),('Lipostat',0),('Liqufilm Tears',0),('Liquid Paraffin',0),('Liquid Paraffin/Acetylated Wool Alcohols',0),('Liquid Paraffin/Isopropyl Myristate',0),('Liquid Paraffin/White Soft Paraffin',0),('Liquid Paraffin/Wool Alcohols/White Soft Paraffin',0),('Liraglutide',0),('Lisinopril',0),('Lisinopril/Hydrochlorothiazide',0),('Liskonum',0),('Lisopress',0),('Litak',0),('Lithium Carbonate',0),('Lithium Citrate',0),('Livial',0),('Loceryl',0),('Locoid',0),('Lodine',0),('Lodoxamide Trometamol',0),('Loestrin',0),('Lofepramine',0),('Lofepramine Hydrochloride',0),('Logynon',0),('Lomont',0),('Lomustine',0),('Loniten',0),('Lopace',0),('Loperamide And Rehydration Powder',0),('Loperamide Hydrochloride',0),('Lopid',0),('Lopinavir/Ritonavir',0),('Loprazolam',0),('Lopresor',0),('Loratadine',0),('Lorazepam',0),('Loron 520',0),('Losartan',0),('Losec',0),('Losec Iv',0),('Losec Mups',0),('Lotemax',0),('Loteprednol Etabonate',0),('Luborant',0),('Lucentis',0),('Lumigan',0),('Lustral',0),('Lutropin Alfa',0),('Luveris',0),('Lyclear Cream Rinse',0),('Lyclear Dermal Cream',0),('Lyflex',0),('Lymecycline',0),('Lypsyl Cold Sore Gel',0),('Lyrica',0),('Lyrinel',0),('Lysine Acetylsalicylate/Metoclopramide Hydrochloride',0),('Lysodren',0),('Lysovir',0),('Maalox',0),('Maalox Plus',0),('Mabcampath',0),('Mabthera',0),('Mackenzies Smelling Salts',0),('Macrobid',0),('Macrodantin',0),('Macrogol 4000',0),('Macrogol Compound Powder Npf',0),('Macugen',0),('Madopar',0),('Magnapen Vial',0),('Magnesium Hydroxide Oral Suspension',0),('Magnesium Hydroxide Tablets',0),('Magnevist',0),('Malarone',0),('Malathion',0),('Mandafen',0),('Manerix',0),('Maraviroc',0),('Marcain Heavy',0),('Marcain Polyamp Steripack',0),('Marevan',0),('Marvelon',0),('Mastaflu',0),('Maxalt',0),('Maxidex',0),('Maxitrol Eye Drops',0),('Maxitrol Eye Ointment',0),('Maxolon',0),('Maxtrex',0),('Mebendazole',0),('Mebeverine Hydrochloride',0),('Mecasermin',0),('Meclozine',0),('Medicated Talc',0),('Medijel Gel',0),('Medijel Pastilles',0),('Medised For Children',0),('Medrone',0),('Medroxyprogesterone Acetate',0),('Mefenamic',0),('Mefenamic Acid',0),('Mefloquine Hydrochloride',0),('Megace',0),('Megestrol Acetate',0),('Meggezones',0),('Meglumine Gadobenate',0),('Meglumine Gadopentetate',0),('Melatonin',0),('Meloxicam',0),('Melphalan',0),('Melphalan Hydrochloride',0),('Memantine Hydrochloride',0),('Menadiol Sodium Phosphate',0),('Meningitec',0),('Menitorix',0),('Menjugate',0),('Menopur',0),('Menotrophin',0),('Menthol Pastilles',0),('Menthol/Anise Oil',0),('Menthol/Camphor/Pine Needle Oil',0),('Menthol/Eucalyptus',0),('Menthol/Peppermint',0),('Menthol/Pine Sylvestris Oil/Abietis Oil',0),('Mepradec',0),('Mepyramine',0),('Merbentyl',0),('Mercaptopurine',0),('Mercilon',0),('Merional',0),('Merocaine',0),('Merocets Lozenges',0),('Merocets Plus',0),('Meronem',0),('Meropenem Trihydrate',0),('Mesalazine',0),('Mesren',0),('Mesterolone',0),('Mestinon',0),('Mestranol/Norethisterone',0),('Metalyse',0),('Meted',0),('Meted Shampoo',0),('Metenix',0),('Metformin',0),('Metformin Hydrochloride',0),('Metformin Hydrochloride/Sitagliptin Phosphate',0),('Metformin Hydrochloride/Vildagliptin',0),('Metformin/Pioglitazone',0),('Methenamine Hippurate',0),('Methotrexate',0),('Methotrexate Sodium',0),('Methoxy Polyethylene Glycol-Epoetin Beta',0),('Methoxymethane/Hydroxyethyl Salicylate/Isopentane',0),('Methyl Aminolevulinate Hydrochloride',0),('Methyl Salicylate',0),('Methyl Salicylate/Menthol',0),('Methyl Salicylate/Menthol/Camphor',0),('Methyl Salicylate/Menthol/Capsicum/Camphor',0),('Methylcellulose',0),('Methylnaltrexone Bromide',0),('Methylphenidate Hydrochloride',0),('Methylprednisolone',0),('Methylprednisolone Acetate',0),('Methylprednisolone Sodium Succinate',0),('Methysergide Maleate',0),('Metipranolol',0),('Metoclopramide',0),('Metoclopramide Hydrochloride',0),('Metoclopramide Hydrochloride/Paracetamol',0),('Metolazone',0),('Metopirone',0),('Metoprolol',0),('Metrogel',0),('Metrolyl',0),('Metronidazole',0),('Metronidazole Benzoate',0),('Metrosa',0),('Metrotop',0),('Metvix',0),('Metyrapone',0),('Miacalcic',0),('Micafungin Sodium',0),('Micardis',0),('Micardisplus',0),('Miconazole',0),('Miconazole Nitrate',0),('Microgynon 30',0),('Micronor',0),('Micropirin',0),('Midazolam Hydrochloride',0),('Mifegyne',0),('Mifepristone',0),('Migard',0),('Migril',0),('Mildison Lipocream',0),('Milrinone',0),('Mimpara',0),('Mini-Plasco Lidocaine',0),('Minijet Adrenaline',0),('Minijet Amiodarone',0),('Minijet Atropine',0),('Minijet Furosemide',0),('Minijet Lidocaine',0),('Minijet Naloxone',0),('Minijet Sodium Bicarbonate',0),('Minims Artificial Tears',0),('Minims Atropine',0),('Minims Chloramphenicol',0),('Minims Cyclopentolate Hydrochloride',0),('Minims Dexamethasone',0),('Minims Lidocaine And Fluorescein',0),('Minims Metipranolol',0),('Minims Pilocarpine Nitrate',0),('Minims Prednisolone',0),('Minims Proxymetacaine And Fluorescein',0),('Minims Tetracaine Hydrochloride',0),('Minims Tropicamide',0),('Minocin',0),('Minocycline Hydrochloride',0),('Minodiab',0),('Minoxidil',0),('Miochol-E',0),('Mirapexin',0),('Mircera',0),('Mirena',0),('Mirtazapine',0),('Misoprostol',0),('Misoprostol/Naproxen',0),('Mitomycin',0),('Mitomycin-C Kyowa',0),('Mitotane',0),('Mitoxantrone Hydrochloride',0),('Mivacron',0),('Mivacurium Chloride',0),('Mixtard',0),('Mizolastine',0),('Mizollen',0),('Mmrvaxpro',0),('Mobiflex',0),('Moclobemide',0),('Modafinil',0),('Modalim',0),('Modecate',0),('Modrenal',0),('Moduret',0),('Moduretic',0),('Moexipril',0),('Moexipril Hydrochloride',0),('Mogadon',0),('Molaxole',0),('Molipaxin',0),('Mometasone',0),('Mometasone Furoate',0),('Monomil',0),('Monosorb',0),('Montelukast Sodium',0),('Morhulin Ointment',0),('Morphine',0),('Motens',0),('Motifene',0),('Motilium',0),('Motilium Tablet',0),('Movelat',0),('Movicol',0),('Moxifloxacin Hydrochloride',0),('Moxisylyte Hydrochloride',0),('Moxonidine',0),('Mucodyne',0),('Mucogel',0),('Multaq',0),('Multi-Action Actifed Tablets',0),('Multihance',0),('Multiparin',0),('Mupirocin Calcium',0),('Muse',0),('Mycamine',0),('Mycil Athletes Foot Spray',0),('Mycil Ointment',0),('Mycil Powder',0),('Mycobutin',0),('Mycophenolate Mofetil',0),('Mycophenolate Mofetil Hydrochloride',0),('Mycophenolate Sodium',0),('Mycota Spray',0),('Myfortic',0),('Myleran',0),('Myocet',0),('Myocrisin',0),('Myotonine',0),('Mysoline',0),('Nabilone',0),('Nabumetone',0),('Nadolol',0),('Nafarelin Acetate',0),('Naftidrofuryl',0),('Naftidrofuryl Oxalate',0),('Nalcrom',0),('Nalidixic Acid',0),('Naloxone Hydrochloride',0),('Nandrolone Decanoate',0),('Naphazoline',0),('Napratec',0),('Naprosyn',0),('Naproxen',0),('Naproxen/Esomeprazole Magnesium Trihydrate',0),('Naramig',0),('Naratriptan Hydrochloride',0),('Naropin',0),('Nasacort',0),('Naseptin',0),('Nasofan',0),('Nasonex',0),('Natalizumab',0),('Natecal D3',0),('Nateglinide',0),('Natracalm',0),('Natrasleep',0),('Natrilix',0),('Natrilix Sr',0),('Navelbine',0),('Nebilet',0),('Nebivolol',0),('Nebivolol Hydrochloride',0),('Nedocromil',0),('Nedocromil Sodium',0),('Nelarabine',0),('Neo-Cytamen',0),('Neo-Naclex',0),('Neoclarityn',0),('Neofel',0),('Neomercazole',0),('Neomycin Sulphate',0),('Neoral',0),('Neorecormon',0),('Neostigmine Metilsulfate',0),('Neostigmine Metilsulfate/Glycopyrronium Bromide',0),('Neotigason',0),('Neulactil',0),('Neulasta',0),('Neupogen',0),('Neupro',0),('Neurobloc',0),('Neurontin',0),('Neutrogena Norwegian Formula Cream',0),('Neutrogena T-Gel Shampoo',0),('Nevirapine',0),('Nevirapine Hemihydrate',0),('Nexavar',0),('Nexium',0),('Nexium Iv',0),('Niaspan',0),('Nicam Gel',0),('Nicardipine',0),('Nicardipine Hydrochloride',0),('Nicorandil',0),('Nicorette Gum',0),('Nicorette Inhalator',0),('Nicorette Invisi Patches',0),('Nicorette Microtab',0),('Nicorette Nasal Spray',0),('Nicorette Patches',0),('Nicotinamide',0),('Nicotine Gum',0),('Nicotine Inhaler',0),('Nicotine Lozenges',0),('Nicotine Nasal Spray',0),('Nicotine Patches',0),('Nicotine Sublingual Tablets',0),('Nicotinell Gum',0),('Nicotinell Lozenges',0),('Nicotinell Patches',0),('Nicotinic Acid',0),('Nifedipine',0),('Nifopress',0),('Night Nurse',0),('Nilotinib Hydrochloride Monohydrate',0),('Nimbex',0),('Nimodipine',0),('Nimotop',0),('Nipent',0),('Niquitin Gum',0),('Niquitin Lozenges',0),('Niquitin Mini Lozenges',0),('Niquitin Patches',0),('Nirolex Chesty Cough Linctus',0),('Nirolex Dry Cough Linctus',0),('Nirolex Dry Cough Relief Lozenges',0),('Nirolex Dry Coughs With Decongestant',0),('Nitrazepam',0),('Nitrofurantoin',0),('Nizatidine',0),('Nizoral',0),('Non-Drowsy Sudafed Childrens Syrup',0),('Nonacog Alfa',0),('Nonoxinol-9',0),('Nootropil',0),('Noradrenaline Acid Tartrate',0),('Norcuron',0),('Norditropin Nordiflex',0),('Norditropin Simplexx',0),('Norethisterone',0),('Norethisterone Enantate',0),('Norfloxacin',0),('Norgalax',0),('Norgeston',0),('Noriday',0),('Norimin',0),('Norimode',0),('Norinyl-1',0),('Noristerat',0),('Normacol',0),('Normacol Plus',0),('Normal Immunoglobulin Human',0),('Nortriptyline',0),('Nortriptyline Hydrochloride',0),('Norvir',0),('Norzol',0),('Novofem',0),('Novomix 30',0),('Novorapid',0),('Novoseven',0),('Noxafil',0),('Nozinan Tablets',0),('Nu-Seals',0),('Nupercainal',0),('Nurofen',0),('Nurofen Cold And Flu',0),('Nurofen Plus',0),('Nutrizym',0),('Nutropinaq',0),('Nuvaring',0),('Nyogel',0),('Nystan',0),('Nystatin',0),('Nytol',0),('Occlusal',0),('Octim',0),('Octocog Alfa',0),('Octreotide Acetate',0),('Ocufen',0),('Oculotect',0),('Ofatumumab',0),('Ofloxacin',0),('Ofloxacin Hydrochloride',0),('Oilatum Cream',0),('Oilatum Emollient',0),('Oilatum Gel',0),('Oilatum Junior Bath Additive',0),('Oilatum Junior Cream',0),('Oilatum Plus',0),('Oilatum Shower Gel Fragrance-Free',0),('Olanzapine',0),('Olanzapine Pamoate Monohydrate',0),('Olbetam',0),('Olmesartan',0),('Olmesartan Medoxomil',0),('Olmetec',0),('Olmetec Plus',0),('Olopatadine Hydrochloride',0),('Olsalazine Sodium',0),('Omalizumab',0),('Omeprazole',0),('Omeprazole Magnesium',0),('Omeprazole Sodium',0),('Oncotice',0),('Ondansetron',0),('Ondansetron Hydrochloride',0),('One-Alpha',0),('Onglyza',0),('Onkotrone',0),('Opatanol',0),('Opilon',0),('Opticrom',0),('Optilast',0),('Optimax',0),('Optivate',0),('Oraldene',0),('Orap',0),('Orelox',0),('Orencia',0),('Orgalutran',0),('Orgaran',0),('Original Andrews Salts',0),('Orlept',0),('Orlistat',0),('Orphenadrine Hydrochloride',0),('Ortho-Gynest',0),('Orudis',0),('Oruvail',0),('Otex',0),('Otomize',0),('Otosporin',0),('Otrivine Adult Measured Dose Sinusitis Spray',0),('Otrivine Adult Menthol Nasal Spray',0),('Otrivine Adult Nasal Drops',0),('Otrivine Adult Nasal Spray',0),('Otrivine Antistin',0),('Otrivine Child Nasal Drops',0),('Otrivine Mu-Cron',0),('Ovestin',0),('Ovitrelle',0),('Ovranette',0),('Ovysmen',0),('Oxactin',0),('Oxaliplatin',0),('Oxcarbazepine',0),('Oxerutins',0),('Oxis',0),('Oxprenolol',0),('Oxprenolol Hydrochloride',0),('Oxprenolol Hydrochloride/Cyclopenthiazide',0),('Oxybuprocaine Hydrochloride',0),('Oxybutynin',0),('Oxybutynin Hydrochloride',0),('Oxymetazoline',0),('Oxytetracycline Dihydrate',0),('Oxytocin',0),('Pabal',0),('Paclitaxel',0),('Paclitaxel Albumin',0),('Pain Relief Balm',0),('Paliperidone',0),('Paliperidone Palmitate',0),('Paludrine',0),('Panadol',0),('Panadol Extra Soluble Tablets',0),('Panadol Extra Tablets',0),('Panadol Night',0),('Pancrease',0),('Pancrex',0),('Pancuronium Bromide',0),('Pandemrix',0),('Panitumumab',0),('Panoxyl Acnegel',0),('Panoxyl Aquagel',0),('Panoxyl Cream',0),('Panoxyl Wash',0),('Pantoprazole',0),('Pantoprazole Sodium Sesquihydrate',0),('Paracetamol',0),('Paracetamol/Caffeine',0),('Paracetamol/Codeine /Caffeine',0),('Paracetamol/Codeine/Diphenhydramine/Caffeine',0),('Paracetamol/Codeine/Doxylamine/Caffeine',0),('Paracetamol/Dihydrocodeine',0),('Paracetamol/Diphenhydramine',0),('Paracetamol/Diphenhydramine Liquid',0),('Paracetamol/Diphenhydramine Tablets',0),('Paracetamol/Phenylephrine Sachets',0),('Paracetamol/Phenylephrine/Caffeine',0),('Paracetamol/Pseudoephedrine',0),('Paracetamol/Sodium Salicylate',0),('Paracetamol/Tramadol Hydrochloride',0),('Paramax',0),('Paramol Soluble Tablets',0),('Paramol Tablets',0),('Parathyroid Hormone',0),('Pardelprin',0),('Parecoxib Sodium',0),('Paricalcitol',0),('Pariet',0),('Parlodel',0),('Parmid',0),('Paroven',0),('Paroxetine',0),('Passion Flower',0),('Passion Flower/Valerian/Hops',0),('Passion Flower/Valerian/Hops/Scullcap/Jamaica Dogwood',0),('Pavacol-D',0),('Paxoran',0),('Pediacel',0),('Pegaptanib Sodium',0),('Pegasys',0),('Pegfilgrastim',0),('Peginterferon Alfa-2A',0),('Peginterferon Alfa-2B (Rbe)',0),('Pegvisomant',0),('Pemetrexed Disodium',0),('Penbritin',0),('Penciclovir',0),('Penicillamine',0),('Pennsaid',0),('Pentasa',0),('Pentostatin',0),('Pentoxifylline',0),('Pentrax Shampoo',0),('Pepcid',0),('Pepcidtwo',0),('Peppermint Oil Capsules',0),('Peppermint Oil/Capsicum/Elder Flower',0),('Peppermint Oil/Cinnamon/Clove Oil/Slippery Elm Bark',0),('Peppermint Oil/Menthol/Benzoin Compound/Ipecacuanha',0),('Peppermint Oil/Menthol/Myrrh',0),('Pepto-Bismol',0),('Perdix',0),('Perfalgan',0),('Pergolide Mesilate',0),('Pergoveris',0),('Periactin',0),('Pericyazine',0),('Perinal Spray',0),('Perindopril',0),('Perindopril Arginine',0),('Permethrin',0),('Persantin',0),('Pevaryl',0),('Pharmaton Capsules',0),('Pharmorubicin',0),('Phenelzine Sulphate',0),('Phenergan',0),('Phenol',0),('Phenol/Aromatic Ammonia/Strong Ammonia',0),('Phenol/Chlorhexidine Digluconate',0),('Phenol/Chlorhexidine Gluconate',0),('Phenylephrine Hydrochloride',0),('Phenylephrine Hydrochloride/Caffeine/Paracetamol',0),('Phenylephrine/Caffeine/Paracetamol Dual Relief',0),('Phenylephrine/Caffeine/Paracetamol Max Strength Capsules',0),('Phenylephrine/Guaifenesin/Paracetamol',0),('Phenylethyl Alcohol/Undecenoic Acid/Cetrimide',0),('Phenytoin',0),('Phenytoin Sodium',0),('Phillips Milk Of Magnesia',0),('Pholcodine',0),('Pholcodine Childrens Oral Solution',0),('Pholcodine Linctus',0),('Phosex',0),('Phyllocontin',0),('Physiotens',0),('Pilocarpine Hydrochloride',0),('Pilocarpine Nitrate',0),('Pimecrolimus',0),('Pimozide',0),('Pindolol',0),('Pinefeld',0),('Pioglitazone',0),('Piperacillin Sodium/Tazobactam Sodium',0),('Piportil',0),('Pipotiazine Palmitate',0),('Piracetam',0),('Piriteze Allergy Syrup',0),('Piriteze Allergy Tablets',0),('Piriton',0),('Piroxicam',0),('Pitressin',0),('Pivmecillinam Hydrochloride',0),('Pizotifen Hydrogen Malate',0),('Plaquenil',0),('Plavix',0),('Plendil',0),('Pletal',0),('Pneumovax Ii',0),('Podophyllotoxin',0),('Pollenshield',0),('Polysaccharide-Iron Complex',0),('Polytar Af Liquid',0),('Polytar Emollient',0),('Polytar Liquid',0),('Polytar Plus Liquid',0),('Polyvinyl Alcohol',0),('Ponstan',0),('Pork Actrapid',0),('Pork Mixtard',0),('Posaconazole',0),('Potassium Citrate',0),('Potassium Citrate/Citric Acid',0),('Potassium Clavulanate/Ticarcillin Sodium',0),('Povidone K25',0),('Povidone-Iodine Spray',0),('Powergel',0),('Pradaxa',0),('Pramipexole Dihydrochloride Monohydrate',0),('Prandin',0),('Prasugrel Hydrochloride',0),('Pravastatin Sodium',0),('Praxilene',0),('Prazosin',0),('Prazosin Hydrochloride',0),('Pred Forte',0),('Predfoam',0),('Prednisolone',0),('Prednisolone Acetate',0),('Prednisolone Sodium Metasulphobenzoate',0),('Prednisolone Sodium Phosphate',0),('Predsol',0),('Pregabalin',0),('Pregnyl',0),('Premarin',0),('Premique',0),('Prempak-C',0),('Preotact',0),('Prescal',0),('Preservex',0),('Prestim',0),('Prevenar',0),('Prezista',0),('Priadel Liquid',0),('Priadel Tablets',0),('Prilocaine Hydrochloride',0),('Prilocaine/Lidocaine',0),('Primacor',0),('Primaxin',0),('Primidone',0),('Primolut N',0),('Primovist',0),('Priorix',0),('Pro-Epanutin',0),('Pro-Viron',0),('Procarbazine Hydrochloride',0),('Prochlorperazine Maleate',0),('Prochlorperazine Mesilate',0),('Procoralan',0),('Proctofoam',0),('Proctosedyl',0),('Procyclidine Hydrochloride',0),('Progesterone',0),('Prograf',0),('Prograf Infusion',0),('Proguanil Hydrochloride',0),('Progynova Patches',0),('Progynova Tablets',0),('Prohance',0),('Proleukin',0),('Prolia',0),('Promethazine',0),('Promethazine Hydrochloride',0),('Promethazine Hydrochloride/Dextromethorphan Hydrobromide/Paracetamol',0),('Promethazine/Dextromethorphan/Paracetamol',0),('Promixin',0),('Propaderm',0),('Propafenone',0),('Propain Caplets',0),('Propain Plus',0),('Propantheline Bromide',0),('Propecia',0),('Propess',0),('Propine',0),('Propiverine Hydrochloride',0),('Propofol',0),('Propranolol',0),('Propranolol Hydrochloride',0),('Proscar',0),('Prostap',0),('Prostin E2',0),('Prosulf',0),('Protamine',0),('Protamine Sulphate',0),('Protelos',0),('Protirelin',0),('Protium',0),('Protopic',0),('Provera',0),('Provigil',0),('Proxymetacaine Hydrochloride',0),('Prozac',0),('Prucalopride Succinate',0),('Pseudoephedrine',0),('Pseudoephedrine Hydrochloride/Diphenhydramine Hydrochloride/Paracetamol',0),('Pseudoephedrine/Acrivastine',0),('Pseudoephedrine/Dextromethorphan',0),('Pseudoephedrine/Paracetamol/Diphenhydramine',0),('Pseudoephedrine/Pholcodine/Paracetamol',0),('Pseudoephedrine/Triprolidine',0),('Pseudoephedrine/Triprolidine/Dextromethorphan',0),('Pseudoephedrine/Triprolidine/Guaifenesin',0),('Psoriderm Bath Additive',0),('Psoriderm Cream',0),('Psoriderm Scalp Lotion',0),('Pulmicort',0),('Pulmozyme',0),('Pumo Bailly',0),('Puregon',0),('Puri-Nethol',0),('Pyralvex',0),('Pyridostigmine Bromide',0),('Pyrimethamine',0),('Questran',0),('Quetiapine Fumarate',0),('Quinapril',0),('Quinapril Hydrochloride',0),('Quinil',0),('Rabeprazole',0),('Rabipur',0),('Ralgex Cream',0),('Ralgex Freeze Spray',0),('Ralgex Heat Spray',0),('Raloxifene Hydrochloride',0),('Raltegravir',0),('Raltitrexed',0),('Ramipril',0),('Ranexa',0),('Ranibizumab',0),('Ranitic',0),('Ranitidine Hydrochloride',0),('Ranitil',0),('Ranolazine',0),('Rapamune',0),('Rapifen',0),('Rapilysin',0),('Rapitil',0),('Rasagiline Mesilate',0),('Rasilez',0),('Rebetol',0),('Rebif',0),('Reboxetine',0),('Reboxetine Mesilate',0),('Rectogesic',0),('Refolinon',0),('Regranex',0),('Regurin',0),('Relcofen',0),('Relenza',0),('Relestat',0),('Relifex',0),('Relistor',0),('Relpax',0),('Remedeine',0),('Remegel',0),('Remegel Wind Relief',0),('Remicade',0),('Remifentanyl Hydrochloride',0),('Reminyl',0),('Renagel',0),('Renvela',0),('Reopro',0),('Repaglinide',0),('Repevax',0),('Replenine-Vf',0),('Requip',0),('Resolor',0),('Resolve',0),('Resolve Extra',0),('Respontin',0),('Restandol',0),('Retalzem',0),('Retapamulin',0),('Reteplase',0),('Retigabine',0),('Retin-A',0),('Retrovir',0),('Revatio',0),('Revaxis',0),('Revlimid',0),('Rexocaine',0),('Reyataz',0),('Rhinocort',0),('Rhinolast',0),('Rhophylac',0),('Rhumalgan',0),('Riamet',0),('Rifabutin',0),('Rifadin',0),('Rifampicin',0),('Rifater',0),('Rifinah',0),('Rilutek',0),('Riluzole',0),('Rimactane',0),('Rimexolone',0),('Rinatec',0),('Rinstead Sugar Free Pastilles',0),('Risedronate Sodium',0),('Risedronate Sodium/Colecalciferol/Calcium Carbonate',0),('Risperdal',0),('Risperidone',0),('Ritalin',0),('Ritonavir',0),('Rituximab',0),('Rivaroxaban',0),('Rivastigmine',0),('Rivastigmine Hydrogen Tartrate',0),('Rivotril',0),('Rizatriptan Benzoate',0),('Roaccutane',0),('Roactemra',0),('Robinul',0),('Robinul-Neostigmine',0),('Robitussin Chesty Cough',0),('Robitussin Chesty Cough With Congestion',0),('Robitussin Dry Cough Medicine',0),('Rocaltrol',0),('Rocephin',0),('Rocuronium Bromide',0),('Roferon-A',0),('Roflumilast',0),('Ropinirole Hydrochloride',0),('Ropivacaine Hydrochloride',0),('Rosiced',0),('Rosuvastatin',0),('Rotarix',0),('Rotigotine',0),('Rozex',0),('Rufinamide',0),('Rupafin',0),('Rupatadine Fumarate',0),('Rynacrom',0),('Rythmodan',0),('Rythmodan Capsules',0),('Sabril',0),('Saflutan',0),('Saizen',0),('Salactol Paint',0),('Salagen',0),('Salatac Gel',0),('Salazopyrin',0),('Salbutamol',0),('Salicylic Acid',0),('Salicylic Acid Ointment',0),('Salicylic Acid Paint',0),('Salicylic Acid/Camphor',0),('Salicylic Acid/Coal Tar/Sulphur',0),('Salicylic Acid/Dithranol',0),('Salicylic Acid/Lactic Acid',0),('Salicylic Acid/Menthol/Ammonium Salicylate/Camphor',0),('Salicylic Acid/Mucopolysaccharide Polysulphate',0),('Salicylic Acid/Rhubarb Extract',0),('Salmeterol',0),('Salofalk',0),('Sandimmun',0),('Sandocal',0),('Sandocal+D',0),('Sandoglobulin Nf',0),('Sandostatin',0),('Sandrena',0),('Sanomigran',0),('Saquinavir Mesilate',0),('Savlon Antiseptic Cream',0),('Savlon Antiseptic Liquid',0),('Savlon Antiseptic Wound Wash',0),('Savlon Bites And Stings Pain Relief Gel',0),('Savlon Dry Spray',0),('Scheriproct',0),('Scholl Athletes Foot Cream',0),('Scholl Athletes Foot Powder',0),('Scholl Callous Removal Pads',0),('Scholl Corn And Callus Removal Liquid',0),('Scholl Corn Removal Plasters (Fabric)',0),('Scholl Corn Removal Plasters (Washproof)',0),('Scholl Polymer Gel Corn Removal Pads',0),('Scholl Seal And Heal Verruca Removal Gel',0),('Scopoderm Tts',0),('Sea-Legs Tablets',0),('Sebivo',0),('Sebomin',0),('Sebren',0),('Sectral',0),('Securon',0),('Selectajet Dopamine',0),('Selegiline Hydrochloride',0),('Selenium Sulphide',0),('Selexid',0),('Senna Fruit/Ispaghula',0),('Senna Syrup',0),('Senna Tablets',0),('Senna/Buckthorn Bark/Psyllium Seeds',0),('Senokot Comfort Tablets',0),('Senokot Dual Relief Tablets',0),('Senokot Hi-Fibre',0),('Senokot Max Strength',0),('Senokot Syrup',0),('Senokot Tablets',0),('Septrin',0),('Seractil',0),('Serc',0),('Serenace',0),('Seretide',0),('Serevent',0),('Seroquel',0),('Seroxat',0),('Sertraline',0),('Sertraline Hydrochloride',0),('Sevelamer Carbonate',0),('Sevelamer Hydrochloride',0),('Sevoflurane',0),('Sildenafil Citrate',0),('Silkis',0),('Silver Nitrate',0),('Simeticone',0),('Simeticone Drops',0),('Simeticone/Loperamide Hydrochloride',0),('Simponi',0),('Simulect',0),('Simvador',0),('Simvastatin',0),('Sinemet',0),('Singulair',0),('Sinthrome',0),('Sinutab Non-Drowsy',0),('Sirolimus',0),('Sitaxentan Sodium',0),('Skelid',0),('Skinoren',0),('Sleepeaze Tablets',0),('Slozem',0),('Sno Tears',0),('Snufflebabe Vapour Rub',0),('Sodiofolin',0),('Sodium Alginate/Calcium Carbonate/Sodium Bicarbonate',0),('Sodium Alginate/Magnesium Alginate',0),('Sodium Alginate/Potassium Bicarbonate',0),('Sodium Aurothiomalate',0),('Sodium Bicarbonate',0),('Sodium Bicarbonate/Citric Acid/Magnesium Sulphate',0),('Sodium Bicarbonate/Dill Seed Oil',0),('Sodium Citrate',0),('Sodium Citrate Compound',0),('Sodium Clodronate',0),('Sodium Cromoglicate',0),('Sodium Feredetate',0),('Sodium Fluoride',0),('Sodium Fluoride/Triclosan',0),('Sodium Fusidate',0),('Sodium Lauryl Ether Sulpho-Succinate/Sodium Lauryl Ether Sulphate',0),('Sodium Oxybate',0),('Sodium Picosulfate',0),('Sodium Pidolate',0),('Sodium Tetradecyl Sulfate',0),('Sodium Valproate',0),('Sofradex Ear/Eye Drops',0),('Solaraze',0),('Solian',0),('Solifenacin Succinate',0),('Solpadeine Headache Soluble Tablets',0),('Solpadeine Headache Tablets',0),('Solpadeine Migraine Ibuprofen And Codeine Tablets',0),('Solu-Cortef',0),('Solu-Medrone',0),('Somatropin',0),('Somatuline',0),('Somavert',0),('Sominex Herbal Tablets',0),('Somnite',0),('Sonata',0),('Sonovue',0),('Sorafenib Tosylate',0),('Sotacor',0),('Sotalol',0),('Sotalol Hydrochloride',0),('Spasmonal',0),('Spasmonal Forte',0),('Spiriva',0),('Spironolactone',0),('Sporanox',0),('Sprycel',0),('Squill/Capsicum',0),('Squill/Pumilio Pine Oil/Ipecacuanha/Liquorice',0),('St. Johns Wort',0),('Stalevo',0),('Stannous Fluoride',0),('Staril',0),('Starlix',0),('Statin',0),('Stavudine',0),('Stelara',0),('Stelazine',0),('Stemetil',0),('Stemetil Tablet',0),('Sterculia',0),('Sterculia/Frangula',0),('Stesolid',0),('Stiemycin',0),('Stilnoct',0),('Strattera',0),('Strepsils',0),('Strepsils Extra Lozenges',0),('Strepsils Orange With Vitamin C',0),('Strepsils Sore Throat And Blocked Nose Lozenges',0),('Streptase',0),('Streptokinase',0),('Stressless Tablets',0),('Stronazon',0),('Strontium Ranelate',0),('Stugeron 15',0),('Sucralfate',0),('Sucrose/Guaifenesin/Cetylpyridinium Chloride/Honey',0),('Sudafed',0),('Sudocrem',0),('Sugammadex Sodium',0),('Sulfadiazine',0),('Sulfamethoxazole/Trimethoprim',0),('Sulfasalazine',0),('Sulphur Hexafluoride',0),('Sulphur/Salicylic Acid',0),('Sulpiride',0),('Sulpor',0),('Sumatriptan',0),('Sumatriptan Succinate',0),('Sunitinib Malate',0),('Supralip',0),('Suprax',0),('Suprecur',0),('Suprefact',0),('Sure-Amp Lidocaine',0),('Surgam',0),('Surmontil',0),('Sustiva',0),('Sutent',0),('Suxamethonium Chloride',0),('Symbicort',0),('Symmetrel',0),('Synarel',0),('Syner-Kinase',0),('Synflorix',0),('Synphase',0),('Syntocinon',0),('Syntometrine',0),('Syprol',0),('Sytron',0),('Tabphyn',0),('Tacrolimus',0),('Tadalafil',0),('Tafluprost',0),('Tagamet',0),('Tambocor',0),('Tamiflu',0),('Tamoxifen Citrate',0),('Tamsulosin Hydrochloride',0),('Tarceva',0),('Targocid',0),('Targretin',0),('Tarivid',0),('Tarivid Injection',0),('Tarka',0),('Tasigna',0),('Tavanic',0),('Tavegil',0),('Taxol',0),('Taxotere',0),('Tazarotene',0),('Tazocin',0),('Tcp Antiseptic Cream',0),('Tcp Antiseptic Liquid',0),('Tcp Antiseptic Ointment',0),('Tcp Sore Throat Lozenges',0),('Tears Naturale',0),('Tegafur/Uracil',0),('Tegretol',0),('Teicoplanin',0),('Telbivudine',0),('Telfast',0),('Telithromycin',0),('Telmisartan',0),('Telzir',0),('Temazepam',0),('Temodal',0),('Temozolomide',0),('Temsirolimus',0),('Tenecteplase',0),('Tenif',0),('Tenofovir Disoproxil Fumarate',0),('Tenoret',0),('Tenoretic',0),('Tenormin',0),('Tenoxicam',0),('Tensipine',0),('Terazosin',0),('Terazosin Hydrochloride',0),('Terbinafine Hydrochloride',0),('Terbutaline',0),('Teriparatide',0),('Tetanus Immunoglobulin Human',0),('Tetracaine Hydrochloride',0),('Tetracycline Hydrochloride',0),('Tetralysal',0),('Teveten',0),('Thelin',0),('Theophylline',0),('Thiopental Sodium',0),('Throaties Strong Original Pastilles',0),('Thurfyl Salicylate/Hexyl Nicotinate/Ethyl Nicotinate',0),('Thwart',0),('Thymoglobuline',0),('Thyrogen',0),('Thyrotropin Alfa',0),('Tiagabine Hydrochloride Monohydrate',0),('Tiaprofenic Acid',0),('Tibolone',0),('Ticagrelor',0),('Ticovac',0),('Tigecycline',0),('Tiger Balm Red',0),('Tiger Balm White',0),('Tilade',0),('Tildiem',0),('Tiloket',0),('Tiloryth',0),('Tiludronate Disodium',0),('Timentin',0),('Timodine',0),('Timolol',0),('Timolol Maleate',0),('Timolol Maleate/Travoprost',0),('Timoptol',0),('Tinidazole',0),('Tinzaparin',0),('Tioconazole',0),('Tioguanine',0),('Tiotropium',0),('Tipranavir',0),('Tirofiban',0),('Tirofiban Hydrochloride',0),('Tixylix Baby Syrup',0),('Tixylix Chesty Cough',0),('Tixylix Dry Cough',0),('Tixylix Honey, Lemon And Glycerol Syrup',0),('Tixylix Toddler Syrup',0),('Tizanidine',0),('Tobi',0),('Tobradex',0),('Tobramycin',0),('Tocilizumab',0),('Toctino',0),('Tolcapone',0),('Tolfenamic Acid',0),('Tolnaftate',0),('Tolnaftate/Benzalkonium Chloride',0),('Tolnaftate/Chlorhexidine',0),('Tolterodine Tartrate',0),('Tomudex',0),('Topal Chewable Tablets',0),('Topamax',0),('Topiramate',0),('Topotecan Hydrochloride',0),('Torasemide',0),('Torem',0),('Toremifene Citrate',0),('Torisel',0),('Toviaz',0),('Tracleer',0),('Tracrium',0),('Tractocile',0),('Tramacet',0),('Tramadol Hydrochloride',0),('Trandolapril',0),('Trandolapril/Verapamil',0),('Trandolapril/Verapamil Hydrochloride',0),('Tranexamic Acid',0),('Transiderm-Nitro',0),('Trasicor',0),('Trasidrex',0),('Trastuzumab',0),('Travatan',0),('Travoprost',0),('Traxam',0),('Trazodone',0),('Trazodone Hydrochloride',0),('Trental',0),('Treosulfan',0),('Tretinoin',0),('Triadene',0),('Triamcinolone',0),('Triamcinolone Acetonide',0),('Triamterene/Hydrochlorothiazide',0),('Triapin',0),('Tridestra',0),('Trifluoperazine Hydrochloride',0),('Trihexyphenidyl Hydrochloride',0),('Trileptal',0),('Trilostane',0),('Trimethoprim',0),('Trimipramine',0),('Trimipramine Maleate',0),('Trimovate',0),('Trinordiol',0),('Trinovum',0),('Tripotassium Dicitratobismuthate',0),('Triptorelin Acetate',0),('Trisenox',0),('Trisequens',0),('Tritace',0),('Trizivir',0),('Trobalt',0),('Tropicamide',0),('Trospium Chloride',0),('Trosyl',0),('Trusopt',0),('Truvada',0),('Tryptophan',0),('Tums Antacid Tablets',0),('Turpentine Oil/Acetic Acid',0),('Turpentine/Dilute Ammonia/Acetic Acid',0),('Twinrix',0),('Tygacil',0),('Tylex',0),('Typherix',0),('Typhim Vi',0),('Typhoid Vaccine',0),('Tyrozets',0),('Tysabri',0),('Tyverb',0),('Ubretid',0),('Uftoral',0),('Ulipristal Acetate',0),('Ultiva',0),('Ultra Chloraseptic Anaesthetic Throat Spray',0),('Ultrabase',0),('Ultramol Soluble Tablets',0),('Undecenoic Acid/Dichlorophen',0),('Unguentum M',0),('Uniroid Hc',0),('Univer',0),('Urdox',0),('Urea',0),('Urea Hydrogen Peroxide',0),('Urea/Lauromacrogols',0),('Urispas',0),('Urokinase',0),('Ursodeoxycholic Acid',0),('Ursofalk',0),('Ursogal',0),('Ustekinumab',0),('Utinor',0),('Utovlan',0),('Vagifem',0),('Valaciclovir Hydrochloride',0),('Valcyte',0),('Valdoxan',0),('Valerian/Hops',0),('Valganciclovir Hydrochloride',0),('Vallergan',0),('Valoid',0),('Valproate Semisodium',0),('Valsartan',0),('Valtrex',0),('Vancomycin Hydrochloride',0),('Vaniqa',0),('Vaqta',0),('Vardenafil Hydrochloride Trihydrate',0),('Varenicline Tartrate',0),('Varicella-Zoster Vaccine',0),('Varilrix',0),('Vascace',0),('Vascalpha',0),('Vasogen',0),('Vectavir',0),('Vectibix',0),('Vecuronium Bromide',0),('Velcade',0),('Velosulin',0),('Vemurafenib',0),('Venlafaxine',0),('Venlafaxine Hydrochloride',0),('Venofer',0),('Ventavis',0),('Ventolin',0),('Vepesid',0),('Vera-Til',0),('Verapamil',0),('Verapamil Hydrochloride',0),('Vermox',0),('Versatis',0),('Vertab',0),('Verteporfin',0),('Vervain/Valerian/Scullcap/Hops',0),('Vervain/Valerian/Scullcap/Hops/Lupulus',0),('Vesanoid',0),('Vesicare',0),('Vexol',0),('Vfend',0),('Viagra',0),('Viatim',0),('Viazem',0),('Vibramycin',0),('Vibramycin-D',0),('Vibrio Cholerae',0),('Vicks Cough Syrup For Chesty Coughs',0),('Vicks Inhaler',0),('Vicks Medinite Syrup',0),('Vicks Sinex Decongestant Nasal Spray',0),('Vicks Sinex Micromist',0),('Vicks Sinex Soother',0),('Vicks Vaporub',0),('Victoza',0),('Victrelis',0),('Videx',0),('Vigabatrin',0),('Vigam',0),('Vildagliptin',0),('Vimovo',0),('Vimpat',0),('Vinblastine',0),('Vinblastine Sulphate',0),('Vincristine Sulphate',0),('Vinflunine Ditartrate',0),('Vinorelbine Tartrate',0),('Viraferon',0),('Viraferonpeg',0),('Viramune',0),('Viramune Suspension',0),('Viread',0),('Viridal',0),('Viscotears',0),('Viskaldix',0),('Visken',0),('Vistide',0),('Visudyne',0),('Vivotif',0),('Volibris',0),('Voltarol',0),('Voltarol Dispersible',0),('Voltarol Emulgel',0),('Voltarol Gel Patch',0),('Voltarol Rapid',0),('Voriconazole',0),('Votrient',0),('Warfarin',0),('Warticon',0),('Wasp-Eze Spray',0),('Waxsol',0),('White Soft Paraffin',0),('White Soft Paraffin/Light Liquid Paraffin',0),('White Soft Paraffin/Liquid Paraffin',0),('Wind-Eze Gel Caps',0),('Wind-Eze Tablets',0),('Windsetlers',0),('Witch Doctor Gel',0),('Witch Hazel Gel',0),('Woodwards Gripe Water',0),('Xalacom',0),('Xalatan',0),('Xamiol',0),('Xanax',0),('Xarelto',0),('Xatral',0),('Xeloda',0),('Xenical',0),('Xeplion',0),('Xigris',0),('Xipamide',0),('Xismox',0),('Xolair',0),('Xylocaine With Adrenaline',0),('Xylometazoline',0),('Xyloproct',0),('Xyrem',0),('Xyzal',0),('Yasmin',0),('Yeast Plasmolysate',0),('Yentreve',0),('Zacin',0),('Zaditen',0),('Zafirlukast',0),('Zaleplon',0),('Zamadol',0),('Zanaflex',0),('Zanamivir',0),('Zanidip',0),('Zantac',0),('Zaponex',0),('Zarontin',0),('Zavedos',0),('Zeasorb',0),('Zebinix',0),('Zeffix',0),('Zelboraf',0),('Zemplar',0),('Zemtard',0),('Zerit',0),('Zestoretic',0),('Zestril',0),('Ziagen',0),('Zibor',0),('Zidoval',0),('Zidovudine',0),('Zimovane',0),('Zinacef',0),('Zinc Oxide/Bismuth Subgallate/Peru Balsam/Bismuth Oxide',0),('Zinc Oxide/Cod Liver Oil',0),('Zinc Oxide/Lidocaine',0),('Zinc Oxide/Lidocaine/Benzoic Acid/Cinnamic Acid/Bismuth Oxide',0),('Zinc Oxide/Peru Balsam/Bismuth Oxide',0),('Zinc Paste/Calamine',0),('Zinc Undecenoate/Undecenoic Acid',0),('Zineryt',0),('Zinnat',0),('Zirtek Allergy Liquid',0),('Zirtek Allergy Tablets',0),('Zispin Soltab',0),('Zithromax',0),('Zocor',0),('Zofran',0),('Zofran Melt',0),('Zofran Suppository',0),('Zoladex',0),('Zoledronic Acid Monohydrate',0),('Zolmitriptan',0),('Zolpidem',0),('Zolpidem Tartrate',0),('Zolvera',0),('Zomacton',0),('Zomig',0),('Zonegran',0),('Zonisamide',0),('Zopiclone',0),('Zorac',0),('Zoton',0),('Zovirax',0),('Zovirax I.V.',0),('Zuclopenthixol Acetate',0),('Zuclopenthixol Decanoate',0),('Zuclopenthixol Dihydrochloride',0),('Zumenon',0),('Zyban',0),('Zyloric',0),('Zyomet',0),('Zypadhera',0),('Zyprexa',0),('Zyvox',0);
/*!40000 ALTER TABLE `medications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `new_patients`
--

DROP TABLE IF EXISTS `new_patients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `new_patients` (
  `serialno` int(11) NOT NULL,
  `sname` varchar(30) DEFAULT NULL,
  `fname` varchar(30) DEFAULT NULL,
  `title` varchar(30) DEFAULT NULL,
  `sex` char(1) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `addr1` varchar(30) NOT NULL DEFAULT '',
  `addr2` varchar(30) NOT NULL DEFAULT '',
  `addr3` varchar(30) NOT NULL DEFAULT '',
  `town` varchar(30) NOT NULL DEFAULT '',
  `county` varchar(30) NOT NULL DEFAULT '',
  `pcde` varchar(30) NOT NULL DEFAULT '',
  `tel1` varchar(30) NOT NULL DEFAULT '',
  `tel2` varchar(30) NOT NULL DEFAULT '',
  `mobile` varchar(30) NOT NULL DEFAULT '',
  `fax` varchar(30) NOT NULL DEFAULT '',
  `email1` varchar(50) NOT NULL DEFAULT '',
  `email2` varchar(50) NOT NULL DEFAULT '',
  `occup` varchar(30) NOT NULL DEFAULT '',
  `nhsno` varchar(30) NOT NULL DEFAULT '',
  `cnfd` date DEFAULT NULL,
  `cset` varchar(10) DEFAULT NULL,
  `dnt1` smallint(6) DEFAULT NULL,
  `dnt2` smallint(6) DEFAULT NULL,
  `courseno0` int(11) DEFAULT NULL,
  `billdate` date DEFAULT NULL,
  `billct` tinyint(3) unsigned DEFAULT NULL,
  `billtype` char(1) DEFAULT NULL,
  `familyno` int(11) DEFAULT NULL,
  `memo` varchar(255) NOT NULL DEFAULT '',
  `status` varchar(30) NOT NULL DEFAULT '',
  PRIMARY KEY (`serialno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `new_patients`
--

LOCK TABLES `new_patients` WRITE;
/*!40000 ALTER TABLE `new_patients` DISABLE KEYS */;
INSERT INTO `new_patients` VALUES (1,'PATIENT','EXAMPLE','MR','M','1969-12-09','19 UNION STREET','','','INVERNESS','SCOTLAND, UK','IV1 1PP','','','','','','','','',NULL,'P',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'','');
/*!40000 ALTER TABLE `new_patients` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `newdocsprinted`
--

DROP TABLE IF EXISTS `newdocsprinted`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `newdocsprinted` (
  `ix` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `serialno` int(11) DEFAULT NULL,
  `printdate` date DEFAULT NULL,
  `docname` varchar(64) DEFAULT NULL,
  `docversion` smallint(6) DEFAULT NULL,
  `data` blob,
  PRIMARY KEY (`ix`),
  KEY `newdocsprinted_serialno_index` (`serialno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `newdocsprinted`
--

LOCK TABLES `newdocsprinted` WRITE;
/*!40000 ALTER TABLE `newdocsprinted` DISABLE KEYS */;
/*!40000 ALTER TABLE `newdocsprinted` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `newestimates`
--

DROP TABLE IF EXISTS `newestimates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `newestimates` (
  `ix` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `serialno` int(11) NOT NULL,
  `courseno` int(10) unsigned DEFAULT NULL,
  `category` char(12) DEFAULT NULL,
  `type` char(20) DEFAULT NULL,
  `number` tinyint(4) DEFAULT NULL,
  `itemcode` char(5) DEFAULT NULL,
  `description` char(50) DEFAULT NULL,
  `fee` int(11) DEFAULT NULL,
  `ptfee` int(11) DEFAULT NULL,
  `csetype` char(5) DEFAULT NULL,
  `feescale` char(1) DEFAULT NULL,
  `dent` tinyint(1) DEFAULT NULL,
  `completed` tinyint(1) DEFAULT NULL,
  `carriedover` tinyint(1) DEFAULT NULL,
  `linked` tinyint(1) DEFAULT NULL,
  `modified_by` varchar(20) NOT NULL,
  `time_stamp` datetime NOT NULL,
  PRIMARY KEY (`ix`),
  KEY `serialno` (`serialno`),
  KEY `courseno` (`courseno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `newestimates`
--

LOCK TABLES `newestimates` WRITE;
/*!40000 ALTER TABLE `newestimates` DISABLE KEYS */;
/*!40000 ALTER TABLE `newestimates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `newfeetable`
--

DROP TABLE IF EXISTS `newfeetable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `newfeetable` (
  `ix` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `section` smallint(6) DEFAULT NULL,
  `USERCODE` char(14) DEFAULT NULL,
  `code` char(8) DEFAULT NULL,
  `oldcode` char(12) DEFAULT NULL,
  `regulation` char(50) DEFAULT NULL,
  `max_per_course` char(25) DEFAULT NULL,
  `description` char(60) DEFAULT NULL,
  `description1` char(60) DEFAULT NULL,
  `NF08` int(11) DEFAULT NULL,
  `NF08_pt` int(11) DEFAULT NULL,
  `PFA` int(11) DEFAULT NULL,
  `NF09` int(11) DEFAULT NULL,
  `NF09_pt` int(11) DEFAULT NULL,
  PRIMARY KEY (`ix`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `newfeetable`
--

LOCK TABLES `newfeetable` WRITE;
/*!40000 ALTER TABLE `newfeetable` DISABLE KEYS */;
/*!40000 ALTER TABLE `newfeetable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `opid`
--

DROP TABLE IF EXISTS `opid`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `opid` (
  `id` char(5) NOT NULL,
  `serialno` int(11) DEFAULT NULL,
  `active` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `fk_opid_serialno` (`serialno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `opid`
--

LOCK TABLES `opid` WRITE;
/*!40000 ALTER TABLE `opid` DISABLE KEYS */;
INSERT INTO `opid` VALUES ('REC',NULL,1),('USER',NULL,1);
/*!40000 ALTER TABLE `opid` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patient_dates`
--

DROP TABLE IF EXISTS `patient_dates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `patient_dates` (
  `pt_sno` int(11) NOT NULL,
  `pd0` date DEFAULT NULL,
  `pd1` date DEFAULT NULL,
  `pd2` date DEFAULT NULL,
  `pd3` date DEFAULT NULL,
  `pd4` date DEFAULT NULL,
  `pd5` date DEFAULT NULL,
  `pd6` date DEFAULT NULL,
  `pd7` date DEFAULT NULL,
  `pd8` date DEFAULT NULL,
  `pd9` date DEFAULT NULL,
  `pd10` date DEFAULT NULL,
  `pd11` date DEFAULT NULL,
  `pd12` date DEFAULT NULL,
  `pd13` date DEFAULT NULL,
  `pd14` date DEFAULT NULL,
  UNIQUE KEY `pt_sno` (`pt_sno`),
  CONSTRAINT `patient_dates_ibfk_1` FOREIGN KEY (`pt_sno`) REFERENCES `new_patients` (`serialno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patient_dates`
--

LOCK TABLES `patient_dates` WRITE;
/*!40000 ALTER TABLE `patient_dates` DISABLE KEYS */;
INSERT INTO `patient_dates` VALUES (1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `patient_dates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patient_money`
--

DROP TABLE IF EXISTS `patient_money`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `patient_money` (
  `pt_sno` int(11) NOT NULL,
  `money0` int(11) NOT NULL DEFAULT '0',
  `money1` int(11) NOT NULL DEFAULT '0',
  `money2` int(11) NOT NULL DEFAULT '0',
  `money3` int(11) NOT NULL DEFAULT '0',
  `money4` int(11) NOT NULL DEFAULT '0',
  `money5` int(11) NOT NULL DEFAULT '0',
  `money6` int(11) NOT NULL DEFAULT '0',
  `money7` int(11) NOT NULL DEFAULT '0',
  `money8` int(11) NOT NULL DEFAULT '0',
  `money9` int(11) NOT NULL DEFAULT '0',
  `money10` int(11) NOT NULL DEFAULT '0',
  `money11` int(11) NOT NULL DEFAULT '0',
  UNIQUE KEY `pt_sno` (`pt_sno`),
  CONSTRAINT `patient_money_ibfk_1` FOREIGN KEY (`pt_sno`) REFERENCES `new_patients` (`serialno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patient_money`
--

LOCK TABLES `patient_money` WRITE;
/*!40000 ALTER TABLE `patient_money` DISABLE KEYS */;
INSERT INTO `patient_money` VALUES (1,0,0,0,0,0,0,0,0,0,0,0,0);
/*!40000 ALTER TABLE `patient_money` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patient_nhs`
--

DROP TABLE IF EXISTS `patient_nhs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `patient_nhs` (
  `pt_sno` int(11) NOT NULL,
  `initaccept` date DEFAULT NULL,
  `lastreaccept` date DEFAULT NULL,
  `lastclaim` date DEFAULT NULL,
  `expiry` date DEFAULT NULL,
  `cstatus` tinyint(3) unsigned DEFAULT NULL,
  `transfer` date DEFAULT NULL,
  `pstatus` tinyint(3) unsigned DEFAULT NULL,
  UNIQUE KEY `pt_sno` (`pt_sno`),
  CONSTRAINT `patient_nhs_ibfk_1` FOREIGN KEY (`pt_sno`) REFERENCES `new_patients` (`serialno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patient_nhs`
--

LOCK TABLES `patient_nhs` WRITE;
/*!40000 ALTER TABLE `patient_nhs` DISABLE KEYS */;
/*!40000 ALTER TABLE `patient_nhs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `perio`
--

DROP TABLE IF EXISTS `perio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `perio` (
  `serialno` int(11) NOT NULL DEFAULT '0',
  `chartdate` date NOT NULL DEFAULT '0000-00-00',
  `bpe` char(6) DEFAULT NULL,
  `chartdata` blob,
  `flag` tinyint(3) unsigned DEFAULT NULL,
  PRIMARY KEY (`serialno`,`chartdate`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `perio`
--

LOCK TABLES `perio` WRITE;
/*!40000 ALTER TABLE `perio` DISABLE KEYS */;
/*!40000 ALTER TABLE `perio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `phrasebook`
--

DROP TABLE IF EXISTS `phrasebook`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `phrasebook` (
  `clinician_id` int(10) unsigned NOT NULL,
  `phrases` text,
  PRIMARY KEY (`clinician_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phrasebook`
--

LOCK TABLES `phrasebook` WRITE;
/*!40000 ALTER TABLE `phrasebook` DISABLE KEYS */;
/*!40000 ALTER TABLE `phrasebook` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `plandata`
--

DROP TABLE IF EXISTS `plandata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `plandata` (
  `serialno` int(11) NOT NULL,
  `plantype` char(4) DEFAULT NULL,
  `band` char(1) DEFAULT NULL,
  `grosschg` int(11) DEFAULT NULL,
  `discount` int(11) DEFAULT NULL,
  `netchg` int(11) DEFAULT NULL,
  `catcode` char(1) DEFAULT NULL,
  `planjoin` date DEFAULT NULL,
  `regno` int(11) DEFAULT NULL,
  PRIMARY KEY (`serialno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `plandata`
--

LOCK TABLES `plandata` WRITE;
/*!40000 ALTER TABLE `plandata` DISABLE KEYS */;
/*!40000 ALTER TABLE `plandata` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `previous_snames`
--

DROP TABLE IF EXISTS `previous_snames`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `previous_snames` (
  `ix` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `serialno` int(11) DEFAULT NULL,
  `psn` char(40) NOT NULL,
  PRIMARY KEY (`ix`),
  KEY `serialno` (`serialno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `previous_snames`
--

LOCK TABLES `previous_snames` WRITE;
/*!40000 ALTER TABLE `previous_snames` DISABLE KEYS */;
/*!40000 ALTER TABLE `previous_snames` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ptmemos`
--

DROP TABLE IF EXISTS `ptmemos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ptmemos` (
  `ix` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `serialno` int(11) DEFAULT NULL,
  `enabled` tinyint(1) DEFAULT NULL,
  `author` char(5) DEFAULT NULL,
  `type` char(5) DEFAULT NULL,
  `mdate` datetime DEFAULT NULL,
  `expiredate` date DEFAULT NULL,
  `message` char(200) DEFAULT NULL,
  `open` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`ix`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ptmemos`
--

LOCK TABLES `ptmemos` WRITE;
/*!40000 ALTER TABLE `ptmemos` DISABLE KEYS */;
/*!40000 ALTER TABLE `ptmemos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `records_in_use`
--

DROP TABLE IF EXISTS `records_in_use`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `records_in_use` (
  `pt_sno` int(11) unsigned NOT NULL,
  `surgery_number` smallint(6) DEFAULT NULL,
  `op` varchar(24) DEFAULT NULL,
  `locked` tinyint(1) NOT NULL DEFAULT '0',
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `records_in_use`
--

LOCK TABLES `records_in_use` WRITE;
/*!40000 ALTER TABLE `records_in_use` DISABLE KEYS */;
/*!40000 ALTER TABLE `records_in_use` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `referral_centres`
--

DROP TABLE IF EXISTS `referral_centres`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `referral_centres` (
  `ix` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `description` char(64) NOT NULL DEFAULT 'referral',
  `greeting` char(64) NOT NULL DEFAULT 'Dear Sir/Madam',
  `addr1` char(64) NOT NULL DEFAULT '',
  `addr2` char(64) NOT NULL DEFAULT '',
  `addr3` char(64) NOT NULL DEFAULT '',
  `addr4` char(64) NOT NULL DEFAULT '',
  `addr5` char(64) NOT NULL DEFAULT '',
  `addr6` char(64) NOT NULL DEFAULT '',
  `addr7` char(64) NOT NULL DEFAULT '',
  PRIMARY KEY (`ix`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `referral_centres`
--

LOCK TABLES `referral_centres` WRITE;
/*!40000 ALTER TABLE `referral_centres` DISABLE KEYS */;
/*!40000 ALTER TABLE `referral_centres` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `settings`
--

DROP TABLE IF EXISTS `settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `settings` (
  `ix` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `value` varchar(128) DEFAULT NULL,
  `data` text,
  `hostname` varchar(128) DEFAULT NULL,
  `station` char(20) DEFAULT NULL,
  `user` char(20) DEFAULT NULL,
  `modified_by` varchar(20) NOT NULL,
  `time_stamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ix`),
  KEY `value` (`value`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `settings`
--

LOCK TABLES `settings` WRITE;
/*!40000 ALTER TABLE `settings` DISABLE KEYS */;
INSERT INTO `settings` VALUES (1,'wikiurl','http://openmolar.com/wiki',NULL,NULL,NULL,'neil@openmolar.com','2014-06-10 17:52:59'),(2,'Schema_Version','2.9',NULL,NULL,NULL,'neil@openmolar.com','2014-07-01 12:51:30'),(3,'Schema_Version','3.0',NULL,NULL,NULL,'2_9 to 3_0 script','2016-09-14 12:15:42'),(5,'Schema_Version','3.1',NULL,NULL,NULL,'3_0 to 3_1 script','2016-09-14 12:15:45'),(7,'Schema_Version','3.2',NULL,NULL,NULL,'3.1 to 3.2 script','2016-09-14 12:15:48'),(9,'Schema_Version','3.3',NULL,NULL,NULL,'3.2 to 3.3 script','2016-09-14 12:15:50'),(11,'Schema_Version','3.4',NULL,NULL,NULL,'3.3 to 3.4 script','2016-09-14 12:15:52'),(13,'Schema_Version','3.5',NULL,NULL,NULL,'3.4 to 3.5 script','2016-09-14 12:15:56'),(14,'compatible_clients','3.5',NULL,NULL,NULL,'Update script','2016-09-14 12:15:56');
/*!40000 ALTER TABLE `settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `standard_letters`
--

DROP TABLE IF EXISTS `standard_letters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `standard_letters` (
  `ix` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `description` char(64) NOT NULL,
  `body_text` text NOT NULL,
  `footer` text,
  PRIMARY KEY (`ix`),
  UNIQUE KEY `description` (`description`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `standard_letters`
--

LOCK TABLES `standard_letters` WRITE;
/*!40000 ALTER TABLE `standard_letters` DISABLE KEYS */;
INSERT INTO `standard_letters` VALUES (1,'XRay Request Letter','<br />\n<div align=\"center\"><b>XRAY REQUEST</b></div>\n<br />\n<p>You have requested copies of your xrays to take with you to another practice.<br />\nPlease be advise that we are happy to do this, and provide these as Jpeg files on CD-rom.\n</p>\n<p>\nThere is, however, a nominal charge of &pound;15.00 for this service, which is in line with British Dental Association recommendations.\n</p>\n<p>\nShould you wish to proceed, please complete the slip below and return it to us along with your remittance.\nOn receipt of the slip, your xrays will normally be forwarded with 7 working days.\n</p>','\n<br />\n<hr />\n<br />\n<p>\nI hereby request copies of my radiographs be sent to:<br />\n(delete as appropriate)\n<ul>\n<li>\nMy home address (as above)\n</li>\n<li>\nAnother dental practice (please give details overleaf).\n</li>\n</ul>\n</p>\n<p>\nI enclose a cheque for &pound; 15.00\n</p>\n<pre>\nSigned    ________________________________________________\n\nDate      ________________________________________________\n\n{{NAME}}\n(adp number {{SERIALNO}}))\n</pre>\n');
/*!40000 ALTER TABLE `standard_letters` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `static_chart`
--

DROP TABLE IF EXISTS `static_chart`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `static_chart` (
  `pt_sno` int(11) NOT NULL,
  `dent0` tinyint(4) DEFAULT NULL,
  `dent1` tinyint(4) DEFAULT NULL,
  `dent2` tinyint(4) DEFAULT NULL,
  `dent3` tinyint(4) DEFAULT NULL,
  `ur1` varchar(34) NOT NULL DEFAULT '',
  `ur2` varchar(34) NOT NULL DEFAULT '',
  `ur3` varchar(34) NOT NULL DEFAULT '',
  `ur4` varchar(34) NOT NULL DEFAULT '',
  `ur5` varchar(34) NOT NULL DEFAULT '',
  `ur6` varchar(34) NOT NULL DEFAULT '',
  `ur7` varchar(34) NOT NULL DEFAULT '',
  `ur8` varchar(34) NOT NULL DEFAULT '',
  `ul1` varchar(34) NOT NULL DEFAULT '',
  `ul2` varchar(34) NOT NULL DEFAULT '',
  `ul3` varchar(34) NOT NULL DEFAULT '',
  `ul4` varchar(34) NOT NULL DEFAULT '',
  `ul5` varchar(34) NOT NULL DEFAULT '',
  `ul6` varchar(34) NOT NULL DEFAULT '',
  `ul7` varchar(34) NOT NULL DEFAULT '',
  `ul8` varchar(34) NOT NULL DEFAULT '',
  `lr1` varchar(34) NOT NULL DEFAULT '',
  `lr2` varchar(34) NOT NULL DEFAULT '',
  `lr3` varchar(34) NOT NULL DEFAULT '',
  `lr4` varchar(34) NOT NULL DEFAULT '',
  `lr5` varchar(34) NOT NULL DEFAULT '',
  `lr6` varchar(34) NOT NULL DEFAULT '',
  `lr7` varchar(34) NOT NULL DEFAULT '',
  `lr8` varchar(34) NOT NULL DEFAULT '',
  `ll1` varchar(34) NOT NULL DEFAULT '',
  `ll2` varchar(34) NOT NULL DEFAULT '',
  `ll3` varchar(34) NOT NULL DEFAULT '',
  `ll4` varchar(34) NOT NULL DEFAULT '',
  `ll5` varchar(34) NOT NULL DEFAULT '',
  `ll6` varchar(34) NOT NULL DEFAULT '',
  `ll7` varchar(34) NOT NULL DEFAULT '',
  `ll8` varchar(34) NOT NULL DEFAULT '',
  UNIQUE KEY `pt_sno` (`pt_sno`),
  CONSTRAINT `static_chart_ibfk_1` FOREIGN KEY (`pt_sno`) REFERENCES `new_patients` (`serialno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `static_chart`
--

LOCK TABLES `static_chart` WRITE;
/*!40000 ALTER TABLE `static_chart` DISABLE KEYS */;
INSERT INTO `static_chart` VALUES (1,NULL,16,NULL,NULL,'PV ','CR,LAVA ','MI ','B,GL ','MOD ','MO,CO ','','UE ','IM/TIT IM/ABUT  CR,V1 ','','','GI/MOD RT ','','','','UE ','','','','','OL,CO ','B ','FS ','UE ','','','','','','MOL,CO ','','UE ');
/*!40000 ALTER TABLE `static_chart` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `userdata`
--

DROP TABLE IF EXISTS `userdata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `userdata` (
  `serialno` int(11) NOT NULL,
  `data` blob,
  PRIMARY KEY (`serialno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `userdata`
--

LOCK TABLES `userdata` WRITE;
/*!40000 ALTER TABLE `userdata` DISABLE KEYS */;
/*!40000 ALTER TABLE `userdata` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-09-14 17:04:01
