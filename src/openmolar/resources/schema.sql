-- MySQL dump 10.15  Distrib 10.0.28-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: localhost
-- ------------------------------------------------------
-- Server version	10.0.28-MariaDB-2

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
  `xraypl` varchar(86) NOT NULL DEFAULT '',
  `periopl` varchar(86) NOT NULL DEFAULT '',
  `anaespl` varchar(86) NOT NULL DEFAULT '',
  `otherpl` varchar(86) NOT NULL DEFAULT '',
  `ndupl` varchar(86) NOT NULL DEFAULT '',
  `ndlpl` varchar(86) NOT NULL DEFAULT '',
  `odupl` varchar(86) NOT NULL DEFAULT '',
  `odlpl` varchar(86) NOT NULL DEFAULT '',
  `custompl` varchar(86) NOT NULL DEFAULT '',
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
  `xraycmp` varchar(86) NOT NULL DEFAULT '',
  `periocmp` varchar(86) NOT NULL DEFAULT '',
  `anaescmp` varchar(86) NOT NULL DEFAULT '',
  `othercmp` varchar(86) NOT NULL DEFAULT '',
  `nducmp` varchar(86) NOT NULL DEFAULT '',
  `ndlcmp` varchar(86) NOT NULL DEFAULT '',
  `oducmp` varchar(86) NOT NULL DEFAULT '',
  `odlcmp` varchar(86) NOT NULL DEFAULT '',
  `customcmp` varchar(86) NOT NULL DEFAULT '',
  `ftr` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`courseno`),
  KEY `serialno` (`serialno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

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
-- Table structure for table `locations`
--

DROP TABLE IF EXISTS `locations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `locations` (
  `serialno` int(11) NOT NULL,
  `location` char(1) DEFAULT NULL,
  PRIMARY KEY (`serialno`),
  CONSTRAINT `locations_ibfk_1` FOREIGN KEY (`serialno`) REFERENCES `new_patients` (`serialno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

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
-- Table structure for table `pseudonyms`
--

DROP TABLE IF EXISTS `pseudonyms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pseudonyms` (
  `ix` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `serialno` int(11) NOT NULL,
  `alt_sname` varchar(30) DEFAULT NULL,
  `alt_fname` varchar(30) DEFAULT NULL,
  `comment` varchar(60) DEFAULT NULL,
  `search_include` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`ix`),
  UNIQUE KEY `serialno` (`serialno`,`alt_sname`,`alt_fname`),
  CONSTRAINT `pseudonyms_ibfk_1` FOREIGN KEY (`serialno`) REFERENCES `new_patients` (`serialno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

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
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-12-13 13:51:43
