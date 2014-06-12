-- MySQL dump 10.13  Distrib 5.5.37, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: new_om_demo
-- ------------------------------------------------------
-- Server version	5.5.37-1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
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
  `maxtime` smallint(6) DEFAULT NULL,
  `flag` tinyint(4) DEFAULT NULL,
  `memo` char(30) DEFAULT NULL,
  `stn` tinyint(4) DEFAULT NULL,
  `ver` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`adate`,`apptix`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aday`
--

LOCK TABLES `aday` WRITE;
/*!40000 ALTER TABLE `aday` DISABLE KEYS */;
/*!40000 ALTER TABLE `aday` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aslot`
--

LOCK TABLES `aslot` WRITE;
/*!40000 ALTER TABLE `aslot` DISABLE KEYS */;
/*!40000 ALTER TABLE `aslot` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cbcodes`
--

LOCK TABLES `cbcodes` WRITE;
/*!40000 ALTER TABLE `cbcodes` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `daybook_link`
--

LOCK TABLES `daybook_link` WRITE;
/*!40000 ALTER TABLE `daybook_link` DISABLE KEYS */;
/*!40000 ALTER TABLE `daybook_link` ENABLE KEYS */;
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
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
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
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
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
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `formatted_notes`
--

LOCK TABLES `formatted_notes` WRITE;
/*!40000 ALTER TABLE `formatted_notes` DISABLE KEYS */;
INSERT INTO `formatted_notes` VALUES (1,1,'2014-06-10','REC',NULL,'opened','System date - 10/06/2014 20:26:37','2014-06-10 19:26:37'),(2,1,'2014-06-10','REC',NULL,'newNOTE','This example patient was added to the demo database today.\n','2014-06-10 19:26:37'),(3,1,'2014-06-10','REC',NULL,'closed','REC 10/06/2014 20:26:37','2014-06-10 19:26:37');
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
  `parent_ix` int(10) unsigned DEFAULT NULL,
  `inits` char(5) DEFAULT NULL,
  `fdate` datetime DEFAULT NULL,
  `topic` char(30) DEFAULT NULL,
  `comment` text NOT NULL,
  `open` tinyint(1) NOT NULL DEFAULT '1',
  `recipient` char(8) DEFAULT NULL,
  PRIMARY KEY (`ix`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forum`
--

LOCK TABLES `forum` WRITE;
/*!40000 ALTER TABLE `forum` DISABLE KEYS */;
/*!40000 ALTER TABLE `forum` ENABLE KEYS */;
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
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forumread`
--

LOCK TABLES `forumread` WRITE;
/*!40000 ALTER TABLE `forumread` DISABLE KEYS */;
/*!40000 ALTER TABLE `forumread` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mednotes`
--

DROP TABLE IF EXISTS `mednotes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mednotes` (
  `serialno` int(11) NOT NULL,
  `drnm` varchar(60) DEFAULT NULL,
  `adrtel` varchar(60) DEFAULT NULL,
  `curmed` varchar(60) DEFAULT NULL,
  `allerg` varchar(60) DEFAULT NULL,
  `heart` varchar(60) DEFAULT NULL,
  `lungs` varchar(60) DEFAULT NULL,
  `liver` varchar(60) DEFAULT NULL,
  `kidney` varchar(60) DEFAULT NULL,
  `bleed` varchar(60) DEFAULT NULL,
  `anaes` varchar(60) DEFAULT NULL,
  `other` varchar(60) DEFAULT NULL,
  `oldmed` varchar(60) DEFAULT NULL,
  `alert` tinyint(1) NOT NULL DEFAULT '0',
  `chkdate` date DEFAULT NULL,
  PRIMARY KEY (`serialno`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mednotes`
--

LOCK TABLES `mednotes` WRITE;
/*!40000 ALTER TABLE `mednotes` DISABLE KEYS */;
/*!40000 ALTER TABLE `mednotes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mnhist`
--

DROP TABLE IF EXISTS `mnhist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mnhist` (
  `serialno` int(11) DEFAULT NULL,
  `chgdate` date DEFAULT NULL,
  `ix` tinyint(3) unsigned DEFAULT NULL,
  `note` varchar(60) DEFAULT NULL,
  KEY `sd` (`serialno`,`chgdate`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mnhist`
--

LOCK TABLES `mnhist` WRITE;
/*!40000 ALTER TABLE `mnhist` DISABLE KEYS */;
/*!40000 ALTER TABLE `mnhist` ENABLE KEYS */;
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
  `docname` char(20) DEFAULT NULL,
  `docversion` smallint(6) DEFAULT NULL,
  `data` blob,
  PRIMARY KEY (`ix`),
  KEY `newdocsprinted_serialno_index` (`serialno`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
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
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
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
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `newfeetable`
--

LOCK TABLES `newfeetable` WRITE;
/*!40000 ALTER TABLE `newfeetable` DISABLE KEYS */;
/*!40000 ALTER TABLE `newfeetable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notes`
--

DROP TABLE IF EXISTS `notes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notes` (
  `serialno` int(11) NOT NULL,
  `lineno` smallint(5) unsigned NOT NULL,
  `line` varchar(80) DEFAULT NULL,
  PRIMARY KEY (`serialno`,`lineno`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notes`
--

LOCK TABLES `notes` WRITE;
/*!40000 ALTER TABLE `notes` DISABLE KEYS */;
/*!40000 ALTER TABLE `notes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `opid`
--

DROP TABLE IF EXISTS `opid`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `opid` (
  `id` char(5) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `opid`
--

LOCK TABLES `opid` WRITE;
/*!40000 ALTER TABLE `opid` DISABLE KEYS */;
INSERT INTO `opid` VALUES ('REC');
INSERT INTO `opid` VALUES ('USER');
/*!40000 ALTER TABLE `opid` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patients`
--

DROP TABLE IF EXISTS `patients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `patients` (
  `serialno` int(11) NOT NULL,
  `pf0` tinyint(4) DEFAULT NULL,
  `pf1` tinyint(4) DEFAULT NULL,
  `pf2` tinyint(4) DEFAULT NULL,
  `pf3` tinyint(4) DEFAULT NULL,
  `pf4` tinyint(4) DEFAULT NULL,
  `pf5` tinyint(4) DEFAULT NULL,
  `pf6` tinyint(4) DEFAULT NULL,
  `pf7` tinyint(4) DEFAULT NULL,
  `pf8` tinyint(4) DEFAULT NULL,
  `pf9` tinyint(4) DEFAULT NULL,
  `pf10` tinyint(4) DEFAULT NULL,
  `pf11` tinyint(4) DEFAULT NULL,
  `pf12` tinyint(4) DEFAULT NULL,
  `pf14` tinyint(4) DEFAULT NULL,
  `pf15` tinyint(4) DEFAULT NULL,
  `pf16` tinyint(4) DEFAULT NULL,
  `pf17` tinyint(4) DEFAULT NULL,
  `pf18` tinyint(4) DEFAULT NULL,
  `pf19` tinyint(4) DEFAULT NULL,
  `money0` int(11) DEFAULT NULL,
  `money1` int(11) DEFAULT NULL,
  `money2` int(11) DEFAULT NULL,
  `money3` int(11) DEFAULT NULL,
  `money4` int(11) DEFAULT NULL,
  `money5` int(11) DEFAULT NULL,
  `money6` int(11) DEFAULT NULL,
  `money7` int(11) DEFAULT NULL,
  `money8` int(11) DEFAULT NULL,
  `money9` int(11) DEFAULT NULL,
  `money10` int(11) DEFAULT NULL,
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
  `sname` varchar(30) DEFAULT NULL,
  `fname` varchar(30) DEFAULT NULL,
  `title` varchar(30) DEFAULT NULL,
  `sex` char(1) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `addr1` varchar(30) DEFAULT NULL,
  `addr2` varchar(30) DEFAULT '',
  `addr3` varchar(30) DEFAULT '',
  `pcde` varchar(30) DEFAULT NULL,
  `tel1` varchar(30) DEFAULT NULL,
  `tel2` varchar(30) DEFAULT NULL,
  `occup` varchar(30) DEFAULT NULL,
  `nhsno` varchar(30) DEFAULT NULL,
  `cnfd` date DEFAULT NULL,
  `cset` varchar(10) DEFAULT NULL,
  `dnt1` smallint(6) DEFAULT NULL,
  `dnt2` smallint(6) DEFAULT NULL,
  `courseno0` int(11) DEFAULT NULL,
  `courseno1` int(11) DEFAULT NULL,
  `exempttext` varchar(50) DEFAULT NULL,
  `ur8st` varchar(34) DEFAULT NULL,
  `ur7st` varchar(34) DEFAULT NULL,
  `ur6st` varchar(34) DEFAULT NULL,
  `ur5st` varchar(34) DEFAULT NULL,
  `ur4st` varchar(34) DEFAULT NULL,
  `ur3st` varchar(34) DEFAULT NULL,
  `ur2st` varchar(34) DEFAULT NULL,
  `ur1st` varchar(34) DEFAULT NULL,
  `ul1st` varchar(34) DEFAULT NULL,
  `ul2st` varchar(34) DEFAULT NULL,
  `ul3st` varchar(34) DEFAULT NULL,
  `ul4st` varchar(34) DEFAULT NULL,
  `ul5st` varchar(34) DEFAULT NULL,
  `ul6st` varchar(34) DEFAULT NULL,
  `ul7st` varchar(34) DEFAULT NULL,
  `ul8st` varchar(34) DEFAULT NULL,
  `ll8st` varchar(34) DEFAULT NULL,
  `ll7st` varchar(34) DEFAULT NULL,
  `ll6st` varchar(34) DEFAULT NULL,
  `ll5st` varchar(34) DEFAULT NULL,
  `ll4st` varchar(34) DEFAULT NULL,
  `ll3st` varchar(34) DEFAULT NULL,
  `ll2st` varchar(34) DEFAULT NULL,
  `ll1st` varchar(34) DEFAULT NULL,
  `lr1st` varchar(34) DEFAULT NULL,
  `lr2st` varchar(34) DEFAULT NULL,
  `lr3st` varchar(34) DEFAULT NULL,
  `lr4st` varchar(34) DEFAULT NULL,
  `lr5st` varchar(34) DEFAULT NULL,
  `lr6st` varchar(34) DEFAULT NULL,
  `lr7st` varchar(34) DEFAULT NULL,
  `lr8st` varchar(34) DEFAULT NULL,
  `dent0` tinyint(4) DEFAULT NULL,
  `dent1` tinyint(4) DEFAULT NULL,
  `dent2` tinyint(4) DEFAULT NULL,
  `dent3` tinyint(4) DEFAULT NULL,
  `exmpt` varchar(10) DEFAULT NULL,
  `dmask` char(7) DEFAULT NULL,
  `minstart` smallint(6) DEFAULT NULL,
  `maxend` smallint(6) DEFAULT NULL,
  `billdate` date DEFAULT NULL,
  `billct` tinyint(3) unsigned DEFAULT NULL,
  `billtype` char(1) DEFAULT NULL,
  `pf20` tinyint(4) DEFAULT NULL,
  `money11` int(11) DEFAULT NULL,
  `pf13` tinyint(4) DEFAULT NULL,
  `familyno` int(11) DEFAULT NULL,
  `memo` varchar(255) DEFAULT NULL,
  `town` varchar(30) DEFAULT '',
  `county` varchar(30) DEFAULT '',
  `mobile` varchar(30) DEFAULT NULL,
  `fax` varchar(30) DEFAULT NULL,
  `email1` varchar(50) DEFAULT NULL,
  `email2` varchar(50) DEFAULT NULL,
  `status` varchar(30) DEFAULT NULL,
  `source` varchar(30) DEFAULT NULL,
  `enrolled` date DEFAULT NULL,
  `archived` tinyint(4) DEFAULT '0',
  `initaccept` date DEFAULT NULL,
  `lastreaccept` date DEFAULT NULL,
  `lastclaim` date DEFAULT NULL,
  `expiry` date DEFAULT NULL,
  `cstatus` tinyint(3) unsigned DEFAULT NULL,
  `transfer` date DEFAULT NULL,
  `pstatus` tinyint(3) unsigned DEFAULT NULL,
  `courseno2` int(11) DEFAULT NULL,
  PRIMARY KEY (`serialno`),
  KEY `sname` (`sname`,`fname`),
  KEY `familyno` (`familyno`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patients`
--

LOCK TABLES `patients` WRITE;
/*!40000 ALTER TABLE `patients` DISABLE KEYS */;
INSERT INTO `patients` VALUES (1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'PATIENT','EXAMPLE','MR','M','1969-12-09','19 UNION STREET','','','IV1 1PP',NULL,NULL,NULL,NULL,NULL,'P',NULL,NULL,NULL,NULL,NULL,'UE ',NULL,'MO,CO ','MOD ','B,GL ','MI ','CR,LAVA ','PV ','IM/TIT IM/ABUT  CR,V1 ',NULL,NULL,'GI/MOD RT ',NULL,NULL,NULL,'UE ','UE ',NULL,'MOL,CO ',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'OL,CO ','B ','FS ','UE ',NULL,16,NULL,NULL,NULL,'YYYYYYY',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'INVERNESS','SCOTLAND, UK',NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `patients` ENABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
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
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `plandata`
--

LOCK TABLES `plandata` WRITE;
/*!40000 ALTER TABLE `plandata` DISABLE KEYS */;
/*!40000 ALTER TABLE `plandata` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `practitioners`
--

DROP TABLE IF EXISTS `practitioners`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `practitioners` (
  `id` smallint(6) NOT NULL DEFAULT '0',
  `inits` char(4) DEFAULT NULL,
  `name` varchar(30) DEFAULT NULL,
  `apptix` smallint(6) DEFAULT NULL,
  `formalname` varchar(30) DEFAULT NULL,
  `fpcno` varchar(20) DEFAULT NULL,
  `quals` varchar(30) DEFAULT NULL,
  `datefrom` date DEFAULT NULL,
  `dateto` date DEFAULT NULL,
  `flag0` tinyint(4) DEFAULT NULL,
  `flag1` tinyint(4) DEFAULT NULL,
  `flag2` tinyint(4) DEFAULT NULL,
  `flag3` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `practitioners`
--

LOCK TABLES `practitioners` WRITE;
/*!40000 ALTER TABLE `practitioners` DISABLE KEYS */;
/*!40000 ALTER TABLE `practitioners` ENABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ptmemos`
--

LOCK TABLES `ptmemos` WRITE;
/*!40000 ALTER TABLE `ptmemos` DISABLE KEYS */;
/*!40000 ALTER TABLE `ptmemos` ENABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `settings`
--

LOCK TABLES `settings` WRITE;
/*!40000 ALTER TABLE `settings` DISABLE KEYS */;
INSERT INTO `settings` VALUES (1,'wikiurl','http://openmolar.com/wiki',NULL,NULL,NULL,'neil@openmolar.com','2014-06-10 17:52:59'),(2,'compatible_clients','2.6',NULL,NULL,NULL,'neil@openmolar.com','2014-06-10 17:53:20'),(3,'Schema_Version','2.6',NULL,NULL,NULL,'neil@openmolar.com','2014-06-10 17:53:35');
/*!40000 ALTER TABLE `settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tasks`
--

DROP TABLE IF EXISTS `tasks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tasks` (
  `ix` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `op` char(8) DEFAULT NULL,
  `author` char(8) DEFAULT NULL,
  `type` char(8) DEFAULT NULL,
  `mdate` datetime NOT NULL,
  `due` datetime NOT NULL,
  `message` char(255) DEFAULT NULL,
  `completed` tinyint(1) NOT NULL DEFAULT '0',
  `visible` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`ix`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tasks`
--

LOCK TABLES `tasks` WRITE;
/*!40000 ALTER TABLE `tasks` DISABLE KEYS */;
/*!40000 ALTER TABLE `tasks` ENABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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

-- Dump completed on 2014-06-10 20:16:01
