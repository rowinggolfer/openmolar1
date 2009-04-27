-- MySQL dump 10.11
--
-- Host: localhost    Database: newdemo
-- ------------------------------------------------------
-- Server version	5.0.67-0ubuntu6

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
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `aday` (
  `adate` date NOT NULL default '0000-00-00',
  `apptix` smallint(6) NOT NULL default '0',
  `start` smallint(6) default NULL,
  `end` smallint(6) default NULL,
  `maxtime` smallint(6) default NULL,
  `flag` tinyint(4) default NULL,
  `memo` char(30) default NULL,
  `stn` tinyint(4) default NULL,
  `ver` tinyint(4) default NULL,
  PRIMARY KEY  (`adate`,`apptix`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `aday`
--

LOCK TABLES `aday` WRITE;
/*!40000 ALTER TABLE `aday` DISABLE KEYS */;
/*!40000 ALTER TABLE `aday` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `apr`
--

DROP TABLE IF EXISTS `apr`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `apr` (
  `serialno` int(11) NOT NULL default '0',
  `aprix` tinyint(4) NOT NULL default '0',
  `practix` smallint(6) default NULL,
  `code0` char(8) default NULL,
  `code1` char(8) default NULL,
  `code2` char(8) default NULL,
  `note` char(20) default NULL,
  `adate` date default NULL,
  `atime` smallint(6) default NULL,
  `length` smallint(6) default NULL,
  `flag0` tinyint(4) default NULL,
  `flag1` tinyint(4) default NULL,
  `flag2` tinyint(4) default NULL,
  `flag3` tinyint(4) default NULL,
  `flag4` tinyint(4) default NULL,
  `datespec` char(10) default NULL,
  PRIMARY KEY  (`serialno`,`aprix`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

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
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `aslot` (
  `adate` date default NULL,
  `apptix` smallint(6) default NULL,
  `start` smallint(6) default NULL,
  `end` smallint(6) default NULL,
  `name` char(30) default NULL,
  `serialno` int(11) default NULL,
  `code0` char(8) default NULL,
  `code1` char(8) default NULL,
  `code2` char(8) default NULL,
  `note` char(20) default NULL,
  `flag0` tinyint(4) default NULL,
  `flag1` tinyint(4) default NULL,
  `flag2` tinyint(4) default NULL,
  `flag3` tinyint(4) default NULL,
  KEY `adate` (`adate`,`apptix`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

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
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `bpe` (
  `serialno` int(11) NOT NULL default '0',
  `bpedate` date NOT NULL default '0000-00-00',
  `bpe` char(6) default NULL,
  PRIMARY KEY  (`serialno`,`bpedate`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `bpe`
--

LOCK TABLES `bpe` WRITE;
/*!40000 ALTER TABLE `bpe` DISABLE KEYS */;
/*!40000 ALTER TABLE `bpe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `calldurr`
--

DROP TABLE IF EXISTS `calldurr`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `calldurr` (
  `stn` tinyint(4) NOT NULL default '0',
  `serialno` int(11) default NULL,
  PRIMARY KEY  (`stn`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

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
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `cashbook` (
  `id` int(11) NOT NULL auto_increment,
  `cbdate` date default NULL,
  `ref` char(10) default NULL,
  `linkid` int(11) default NULL,
  `descr` varchar(32) default NULL,
  `code` tinyint(3) unsigned default NULL,
  `dntid` smallint(6) default NULL,
  `amt` int(11) default NULL,
  PRIMARY KEY  (`id`),
  KEY `date` (`cbdate`),
  KEY `ref` (`ref`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `cashbook`
--

LOCK TABLES `cashbook` WRITE;
/*!40000 ALTER TABLE `cashbook` DISABLE KEYS */;
/*!40000 ALTER TABLE `cashbook` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `currtrtmt`
--

DROP TABLE IF EXISTS `currtrtmt`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `currtrtmt` (
  `serialno` int(11) NOT NULL,
  `courseno` int(11) NOT NULL,
  `xraypl` varchar(56) default NULL,
  `periopl` varchar(56) default NULL,
  `anaespl` varchar(56) default NULL,
  `otherpl` varchar(56) default NULL,
  `ndupl` varchar(56) default NULL,
  `ndlpl` varchar(56) default NULL,
  `odupl` varchar(56) default NULL,
  `odlpl` varchar(56) default NULL,
  `xraycmp` varchar(56) default NULL,
  `periocmp` varchar(56) default NULL,
  `anaescmp` varchar(56) default NULL,
  `othercmp` varchar(56) default NULL,
  `nducmp` varchar(56) default NULL,
  `ndlcmp` varchar(56) default NULL,
  `oducmp` varchar(56) default NULL,
  `odlcmp` varchar(56) default NULL,
  `ur8pl` varchar(34) default NULL,
  `ur7pl` varchar(34) default NULL,
  `ur6pl` varchar(34) default NULL,
  `ur5pl` varchar(34) default NULL,
  `ur4pl` varchar(34) default NULL,
  `ur3pl` varchar(34) default NULL,
  `ur2pl` varchar(34) default NULL,
  `ur1pl` varchar(34) default NULL,
  `ul1pl` varchar(34) default NULL,
  `ul2pl` varchar(34) default NULL,
  `ul3pl` varchar(34) default NULL,
  `ul4pl` varchar(34) default NULL,
  `ul5pl` varchar(34) default NULL,
  `ul6pl` varchar(34) default NULL,
  `ul7pl` varchar(34) default NULL,
  `ul8pl` varchar(34) default NULL,
  `ll8pl` varchar(34) default NULL,
  `ll7pl` varchar(34) default NULL,
  `ll6pl` varchar(34) default NULL,
  `ll5pl` varchar(34) default NULL,
  `ll4pl` varchar(34) default NULL,
  `ll3pl` varchar(34) default NULL,
  `ll2pl` varchar(34) default NULL,
  `ll1pl` varchar(34) default NULL,
  `lr1pl` varchar(34) default NULL,
  `lr2pl` varchar(34) default NULL,
  `lr3pl` varchar(34) default NULL,
  `lr4pl` varchar(34) default NULL,
  `lr5pl` varchar(34) default NULL,
  `lr6pl` varchar(34) default NULL,
  `lr7pl` varchar(34) default NULL,
  `lr8pl` varchar(34) default NULL,
  `ur8cmp` varchar(34) default NULL,
  `ur7cmp` varchar(34) default NULL,
  `ur6cmp` varchar(34) default NULL,
  `ur5cmp` varchar(34) default NULL,
  `ur4cmp` varchar(34) default NULL,
  `ur3cmp` varchar(34) default NULL,
  `ur2cmp` varchar(34) default NULL,
  `ur1cmp` varchar(34) default NULL,
  `ul1cmp` varchar(34) default NULL,
  `ul2cmp` varchar(34) default NULL,
  `ul3cmp` varchar(34) default NULL,
  `ul4cmp` varchar(34) default NULL,
  `ul5cmp` varchar(34) default NULL,
  `ul6cmp` varchar(34) default NULL,
  `ul7cmp` varchar(34) default NULL,
  `ul8cmp` varchar(34) default NULL,
  `ll8cmp` varchar(34) default NULL,
  `ll7cmp` varchar(34) default NULL,
  `ll6cmp` varchar(34) default NULL,
  `ll5cmp` varchar(34) default NULL,
  `ll4cmp` varchar(34) default NULL,
  `ll3cmp` varchar(34) default NULL,
  `ll2cmp` varchar(34) default NULL,
  `ll1cmp` varchar(34) default NULL,
  `lr1cmp` varchar(34) default NULL,
  `lr2cmp` varchar(34) default NULL,
  `lr3cmp` varchar(34) default NULL,
  `lr4cmp` varchar(34) default NULL,
  `lr5cmp` varchar(34) default NULL,
  `lr6cmp` varchar(34) default NULL,
  `lr7cmp` varchar(34) default NULL,
  `lr8cmp` varchar(34) default NULL,
  `examt` varchar(10) default NULL,
  `examd` date default NULL,
  `accd` date default NULL,
  `cmpd` date default NULL,
  PRIMARY KEY  (`serialno`,`courseno`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `currtrtmt`
--

LOCK TABLES `currtrtmt` WRITE;
/*!40000 ALTER TABLE `currtrtmt` DISABLE KEYS */;
/*!40000 ALTER TABLE `currtrtmt` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `daybook`
--

DROP TABLE IF EXISTS `daybook`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `daybook` (
  `date` date default NULL,
  `serialno` int(11) default NULL,
  `coursetype` char(1) default NULL,
  `dntid` smallint(6) default NULL,
  `trtid` smallint(6) default NULL,
  `diagn` varchar(56) default NULL,
  `perio` varchar(56) default NULL,
  `anaes` varchar(56) default NULL,
  `misc` varchar(56) default NULL,
  `ndu` varchar(56) default NULL,
  `ndl` varchar(56) default NULL,
  `odu` varchar(56) default NULL,
  `odl` varchar(56) default NULL,
  `other` varchar(56) default NULL,
  `chart` blob,
  `feesa` int(11) default NULL,
  `feesb` int(11) default NULL,
  `feesc` int(11) default NULL,
  `id` int(10) unsigned NOT NULL auto_increment,
  PRIMARY KEY  (`id`),
  KEY `date` (`date`),
  KEY `serialno` (`serialno`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `daybook`
--

LOCK TABLES `daybook` WRITE;
/*!40000 ALTER TABLE `daybook` DISABLE KEYS */;
/*!40000 ALTER TABLE `daybook` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `docsprinted`
--

DROP TABLE IF EXISTS `docsprinted`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `docsprinted` (
  `serialno` int(11) default NULL,
  `printdate` date default NULL,
  `docname` char(20) default NULL,
  `docversion` smallint(6) default NULL,
  `fieldvalues` mediumblob,
  KEY `sd` (`serialno`,`printdate`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `docsprinted`
--

LOCK TABLES `docsprinted` WRITE;
/*!40000 ALTER TABLE `docsprinted` DISABLE KEYS */;
/*!40000 ALTER TABLE `docsprinted` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `families`
--

DROP TABLE IF EXISTS `families`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `families` (
  `familyno` int(11) NOT NULL,
  `head` int(11) default NULL,
  PRIMARY KEY  (`familyno`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `families`
--

LOCK TABLES `families` WRITE;
/*!40000 ALTER TABLE `families` DISABLE KEYS */;
/*!40000 ALTER TABLE `families` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mednotes`
--

DROP TABLE IF EXISTS `mednotes`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `mednotes` (
  `serialno` int(11) NOT NULL,
  `drnm` varchar(60) default NULL,
  `adrtel` varchar(60) default NULL,
  `curmed` varchar(60) default NULL,
  `allerg` varchar(60) default NULL,
  `heart` varchar(60) default NULL,
  `lungs` varchar(60) default NULL,
  `liver` varchar(60) default NULL,
  `kidney` varchar(60) default NULL,
  `bleed` varchar(60) default NULL,
  `anaes` varchar(60) default NULL,
  `other` varchar(60) default NULL,
  `oldmed` varchar(60) default NULL,
  PRIMARY KEY  (`serialno`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

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
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `mnhist` (
  `serialno` int(11) default NULL,
  `chgdate` date default NULL,
  `ix` tinyint(3) unsigned default NULL,
  `note` varchar(60) default NULL,
  KEY `sd` (`serialno`,`chgdate`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `mnhist`
--

LOCK TABLES `mnhist` WRITE;
/*!40000 ALTER TABLE `mnhist` DISABLE KEYS */;
/*!40000 ALTER TABLE `mnhist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `newfeetable`
--

DROP TABLE IF EXISTS `newfeetable`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `newfeetable` (
  `ix` smallint(5) unsigned NOT NULL auto_increment,
  `section` smallint(6) default NULL,
  `USERCODE` char(20) default NULL,
  `code` char(12) default NULL,
  `oldcode` char(12) default NULL,
  `nhs_note1` char(20) default NULL,
  `max_per_course` char(30) default NULL,
  `description` char(60) default NULL,
  `description1` char(60) default NULL,
  `NF08` int(11) default NULL,
  `NF08_pt` int(11) default NULL,
  `PFA` int(11) default NULL,
  `PFC` int(11) default NULL,
  `PFI` int(11) default NULL,
  `spare1` char(20) default NULL,
  `spare2` char(20) default NULL,
  `spare3` char(20) default NULL,
  `spare4` char(20) default NULL,
  PRIMARY KEY  (`ix`)
) ENGINE=MyISAM AUTO_INCREMENT=495 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `newfeetable`
--

LOCK TABLES `newfeetable` WRITE;
/*!40000 ALTER TABLE `newfeetable` DISABLE KEYS */;
INSERT INTO `newfeetable` VALUES (1,1,'CE','0101','1a','','1','clinical examination^','clinical exam',800,0,1950,1950,0,NULL,NULL,NULL,NULL),(2,1,'ECE','0111','1b','','1','extensive clinical examination^','extensive clinical exam',1200,0,3850,4500,0,NULL,NULL,NULL,NULL),(3,1,'FCA','0121','1c','','1','full case assessment^','full case assessment',2500,0,6655,7500,0,NULL,NULL,NULL,NULL),(4,1,'','0131','1d','','1','care and treatment summary^','care & treatment summary',395,316,0,0,0,NULL,NULL,NULL,NULL),(5,2,'S','0201','2a1','','1','small xray*','small xrays 1 film',395,316,990,1000,0,NULL,NULL,NULL,NULL),(6,2,'2S','0201','','','2','','small xrays 2 films',550,440,1300,1500,0,NULL,NULL,NULL,NULL),(7,2,'3S','0201','','','3','','small xrays 3 films',675,540,1760,2000,0,NULL,NULL,NULL,NULL),(8,2,'aS','0201','','','ADDITIONAL','','small xrays each addnl',180,144,495,500,0,NULL,NULL,NULL,NULL),(9,2,'maxS','0201','','','MAX','','small xrays max for addnl',1630,1304,5610,6000,0,NULL,NULL,NULL,NULL),(10,2,'M','0202','2a2','','1','medium xray*','medium xrays 1 film',520,416,1100,1200,0,NULL,NULL,NULL,NULL),(11,2,'aM','0202','','','ADDITIONAL','','medium xrays each addnl',225,180,715,0,0,NULL,NULL,NULL,NULL),(12,2,'maxM','0202','','','MAX','','medium xrays max for addnl',465,372,4895,5000,0,NULL,NULL,NULL,NULL),(13,2,'L','0202','2a3','','1','large xray*','large xrays 1 film',825,660,0,0,0,NULL,NULL,NULL,NULL),(14,2,'aL','0203','','','ADDITIONAL','','large xrays each addnl',395,316,0,0,0,NULL,NULL,NULL,NULL),(15,2,'maxL','0203','','','MAX','','large xrays max for addnl',785,628,0,0,0,NULL,NULL,NULL,NULL),(16,2,'P','0204','2a4','','1','panoral xray*','panoral xray',1225,98,2900,3000,0,NULL,NULL,NULL,NULL),(17,2,'','0205','2a5','','','ortho lateral headplate xray*','lateral headplates (ortho, per film)',1810,1448,0,0,0,NULL,NULL,NULL,NULL),(18,2,'','0206','2a5','','','lateral headplate xray*','lateral headplates (other, per film)',1465,1172,0,0,0,NULL,NULL,NULL,NULL),(19,2,'SM1','0211','2b','','','set study model*','study models, per set',1770,1416,3850,0,0,NULL,NULL,NULL,NULL),(20,2,'SM2','0212','2b','','','duplicate study model*','study models, per duplicate set',1110,888,2365,0,0,NULL,NULL,NULL,NULL),(21,2,'','0213','2b','','','single study model*','single study model',875,700,2200,0,0,NULL,NULL,NULL,NULL),(22,2,'','0221','2b','','discretionary','occlusal analysis/adjustable articulator^','occlusal analysis/adjustable artic',0,0,0,0,0,NULL,NULL,NULL,NULL),(23,2,'','0207','2c','','','duplicate xray','duplication of panoral films and lat headplates',630,0,0,0,0,NULL,NULL,NULL,NULL),(24,2,'PHO','0301','3','','1','colour photo*','colour photos 1 view',395,316,1265,0,0,NULL,NULL,NULL,NULL),(25,2,'','0301','','','ADDITIONAL','','each addnl view',205,164,1210,0,0,NULL,NULL,NULL,NULL),(26,2,'','0301','','','MAX','','max addnl views',415,332,5500,0,0,NULL,NULL,NULL,NULL),(27,2,'','0601','6','','','preventive/oral hygiene instruction^','preventive instruction (course)',875,700,0,0,0,NULL,NULL,NULL,NULL),(28,2,'','0701','7a','','','preventive fissure sealant*','preventive fissure sealants (tooth)',785,628,0,0,0,NULL,NULL,NULL,NULL),(29,2,'','0711','7b','','','fluoride^','fluoride (course)',3745,2996,0,0,0,NULL,NULL,NULL,NULL),(30,3,'SP','1001','10a','','','scale and polish^','scale & polish',1260,1008,2850,3000,0,NULL,NULL,NULL,NULL),(31,3,'SP+','1011','10b','','','extended scale and polish^','scale & polish > 1 visit',3050,2440,5700,0,0,NULL,NULL,NULL,NULL),(32,3,'','1021','10c','','<5 TEETH','treatment of chronic periodontal disease^','chronic perio > 2 visits 1-4 teeth',3885,3108,4300,0,0,NULL,NULL,NULL,NULL),(33,3,'','1021','','','5-9 TEETH','sextants treated','chronic perio 5-9 teeth',4745,3796,9735,0,0,NULL,NULL,NULL,NULL),(34,3,'','1021','','','10-16 TEETH','','chronic perio 10-16 teeth',5610,4488,11550,0,0,NULL,NULL,NULL,NULL),(35,3,'','1021','','','>16 TEETH','','chronic perio > 16 teeth',6285,5028,12925,0,0,NULL,NULL,NULL,NULL),(36,3,'','1022','10c','','PER SEXTANT','','chronic perio sextant fee',785,628,1595,0,0,NULL,NULL,NULL,NULL),(37,3,'','1041','10e','','discretionary','periodontal splinting^','splinting of compromised teeth',0,0,0,0,0,NULL,NULL,NULL,NULL),(38,3,'','1101','11a','','','(upper) gingivectomy$','gingivectomy, 1st 2 teeth/jaw',2145,1716,0,0,0,NULL,NULL,NULL,NULL),(39,3,'','1102','11a','','','(lower) gingivectomy$','gingivectomy, 1st 2 teeth/jaw',2145,1716,0,0,0,NULL,NULL,NULL,NULL),(40,3,'','1103','','','','gingivectomy additional teeth','gingivectomy, addnl teeth',480,384,0,0,0,NULL,NULL,NULL,NULL),(41,3,'','1103','','','','','gingivectomy, max per visit',4915,3932,0,0,0,NULL,NULL,NULL,NULL),(42,3,'','1111','11b','','','raising (upper) mucoperiosteal flap*','mucoperiost flap, 1st 2 teeth/jaw',4745,3796,0,0,0,NULL,NULL,NULL,NULL),(43,3,'','1112','11b','','','raising (lower) mucoperiosteal flap*','mucoperiost flap, 1st 2 teeth/jaw',4745,3796,0,0,0,NULL,NULL,NULL,NULL),(44,3,'','1113','','','','mucoperiosteal flap additional teeth','mucoperiost flap, addnl teeth',645,516,0,0,0,NULL,NULL,NULL,NULL),(45,3,'','1113','','','','','mucoperiost flap, max per visit',8485,6788,0,0,0,NULL,NULL,NULL,NULL),(46,3,'','1100','11ab','','','sextants treated surgically','both above, addnl sextant fee',785,628,0,0,0,NULL,NULL,NULL,NULL),(47,3,'','1121','11c','','','gingival graft*','gingival graft',7640,6112,0,0,0,NULL,NULL,NULL,NULL),(48,3,'','1131','11d','','','soft tissue excision','excision of soft tissue (tooth)',785,628,5500,0,0,NULL,NULL,NULL,NULL),(49,3,'','1191','11e','','discretionary','periodontal surgery^','other perio surgery',0,0,0,0,0,NULL,NULL,NULL,NULL),(50,4,'','1401','14a1','','','single surface amalgam filling*','amalgam 1 sfce',855,684,4100,5000,0,NULL,NULL,NULL,NULL),(51,4,'','1402','14a2','','','compound amalgam filling*','amalgam > 1 sfce',1260,1008,4700,6000,0,NULL,NULL,NULL,NULL),(52,4,'','1403','14a3','','','mo/do amalgam filling*','amalgam > 1 sfce incl MO/DO',1660,1328,5500,6000,0,NULL,NULL,NULL,NULL),(53,4,'','1404','14a4','','','mod amalgam filling*','amalgam > 2 sfce incl MOD',2195,1756,5500,6000,0,NULL,NULL,NULL,NULL),(54,4,'','1411','14b','','','tunnel restoration*','tunnel restorations',1660,1328,5500,6000,0,NULL,NULL,NULL,NULL),(55,4,'','1412','','','','multiple tunnel restoration*','tunn rests max per tooth',2195,1756,6985,7000,0,NULL,NULL,NULL,NULL),(56,4,'','1415','Ponly','','Private only','1-sfce composite filling*','composite 1 sfce',0,0,5200,6000,0,NULL,NULL,NULL,NULL),(57,4,'','1416','','','Private only','2-sfce composite filling*','composite 2 sfces',0,0,6050,6500,0,NULL,NULL,NULL,NULL),(58,4,'','1417','','','Private only','3-sfce composite filling*','composite 3 sfces',0,0,8000,0,0,NULL,NULL,NULL,NULL),(59,4,'','1418','','','Private only','large composite filling*','composite > 3 sfces',0,0,8000,9000,0,NULL,NULL,NULL,NULL),(60,4,'','1421','14c1','','','1-sfce composite filling*','composite 1 sfce',1610,1288,5200,6000,0,NULL,NULL,NULL,NULL),(61,4,'','1421','','','Private only','2-sfce composite filling*','composite 2 sfces',0,0,6050,6500,0,NULL,NULL,NULL,NULL),(62,4,'','1421','','','Private only','3-sfce composite filling*','composite 3 sfces',0,0,8000,0,0,NULL,NULL,NULL,NULL),(63,4,'','1421','','','Private only','large composite filling*','composite > 3 sfces',0,0,8000,9000,0,NULL,NULL,NULL,NULL),(64,4,'','1420','14c1','','','composite filling*','composite max per tooth',2500,2000,10450,12000,0,NULL,NULL,NULL,NULL),(65,4,'','1422','','','','1 incisal angle','incisal angle',520,416,0,0,0,NULL,NULL,NULL,NULL),(66,4,'','1423','','','','incisal edge','incisal edge',105,84,0,0,0,NULL,NULL,NULL,NULL),(67,4,'','1424','','','','2 incisal angles','2 incisal angles',855,684,0,0,0,NULL,NULL,NULL,NULL),(68,4,'','1425','','','','cusp tip restoration*','buccal cusp tip',1225,980,2695,3000,0,NULL,NULL,NULL,NULL),(69,4,'','1426','14c2','','1','glass ionomer/silicate filling*','glass ionomer/silicate 1 filling',1465,1172,3500,4500,0,NULL,NULL,NULL,NULL),(70,4,'','1427','','','MAX','multiple glass ionomer filling*','glass ion max per tooth',2000,1600,4180,6000,0,NULL,NULL,NULL,NULL),(71,4,'','1431','14d','','','pin/screw retainer*','pin/screw retainer',675,540,1540,1000,0,NULL,NULL,NULL,NULL),(72,4,'','1451','14f','','discretionary','replacement of amalgam fillings^','amalgam replacement',0,0,0,0,0,NULL,NULL,NULL,NULL),(73,4,'','1461','14g','','1','glass ionomer cement treatment','glass ionomer cement filling',1465,1172,3500,4500,0,NULL,NULL,NULL,NULL),(74,4,'','1462','','','MAX','multiple glass cement treatment','glass ion cem, max per tooth',2175,1740,4675,6000,0,NULL,NULL,NULL,NULL),(75,4,'','1470','14','','MAXIMUM','combined fillings (a)','max all restns 1 tooth',3050,2440,12100,12000,0,NULL,NULL,NULL,NULL),(76,4,'','1471','14','','MAXIMUM','combined fillings (b)','max all restns with p/s or comp adds',3395,2716,12100,14000,0,NULL,NULL,NULL,NULL),(77,4,'','1501','15a','','','anterior root filling*','root filling 1-3',4620,3696,10500,14000,0,NULL,NULL,NULL,NULL),(78,4,'','1502','','','','upper premolar root filling*','root filling U 4-5',6290,5032,13600,18000,0,NULL,NULL,NULL,NULL),(79,4,'','1503','','','','lower premolar root filling*','root filling L 4-5',5450,4360,12700,18000,0,NULL,NULL,NULL,NULL),(80,4,'','1504','','','','molar root filling*','root filling 6-8',9665,7732,18000,27000,0,NULL,NULL,NULL,NULL),(81,4,'','1511','15b','','','vital pulpotomy$','vital pulpotomy',1835,1468,3960,6000,0,NULL,NULL,NULL,NULL),(82,4,'','1521','15c','','','incisor/canine apicectomy$','apicectomy 1-3',4080,3264,13970,15000,0,NULL,NULL,NULL,NULL),(83,4,'','1522','','','','premolar apicectomy$','apicectomy 4-5',5610,4488,13970,15000,0,NULL,NULL,NULL,NULL),(84,4,'','1523','','','','buccal molar apicectomy$','apicectomy buccal roots U 6-8',6610,5288,13970,15000,0,NULL,NULL,NULL,NULL),(85,4,'','1531','','','discretionary','other apicectomy$','apicectomy any other',0,0,0,0,0,NULL,NULL,NULL,NULL),(86,4,'','1541','','','','retrograde root filling*','addnl for retro root filling',875,700,0,0,0,NULL,NULL,NULL,NULL),(87,4,'','1551','15d','','','retained deciduous root treatment*','retained deciduous tooth',2280,1824,6985,0,0,NULL,NULL,NULL,NULL),(88,4,'','1601','16','','','porcelain veneer*','porcelain veneer',10185,8148,25000,28000,0,NULL,NULL,NULL,NULL),(89,4,'','1600','','','â€œ1ST','first veneer extra fee','addnl for 1st veneer',785,628,0,0,0,NULL,NULL,NULL,NULL),(90,4,'','1701','17a1','','','single surface gold inlay*','inlay, 1 sfce',6610,5288,30000,0,0,NULL,NULL,NULL,NULL),(91,4,'','1702','','','','compound gold inlay*','inlay, > 1 sfce',9335,7468,30000,0,0,NULL,NULL,NULL,NULL),(92,4,'','1703','','','','compound incisal gold inlay*','inlay, > 1 sfce with inc ang',8485,6788,30000,0,0,NULL,NULL,NULL,NULL),(93,4,'','1704','','','','compound confluent gold inlay*','inlay, compound confluent',12390,9912,30000,0,0,NULL,NULL,NULL,NULL),(94,4,'','1705','','','Private only','gold 3/4 crown*','gold 3/4 crown',0,0,33000,0,0,NULL,NULL,NULL,NULL),(95,4,'','1706','','','Private only','full gold crown*','gold crown',0,0,33000,0,0,NULL,NULL,NULL,NULL),(96,4,'','1711','17b1','','','precious metal alloy crown*','Full or Â¾ pm alloy crown',11035,8828,0,0,0,NULL,NULL,NULL,NULL),(97,4,'','1712','17b2','','','non-precious metal alloy crown*','non-pm alloy crown',8485,6788,0,0,0,NULL,NULL,NULL,NULL),(98,4,'','1716','17c','','','porcelain jacket crown*','porcelain jacket crown',8315,6652,33000,0,0,NULL,NULL,NULL,NULL),(99,4,'','1721','17d1','','NHS â€“ not on molars','gold/precious metal bonded crown*','pm bonded crown',12650,10120,33000,0,0,NULL,NULL,NULL,NULL),(100,4,'','1722','17d2','','NHS â€“ not on molars','non-precious metal bonded crown*','non-pm bonded crown',11360,9088,0,0,0,NULL,NULL,NULL,NULL),(101,4,'','1723','17d3','','NHS â€“ not on molars','platinum bonded crown*','platinum bonded crown',9680,7744,0,0,0,NULL,NULL,NULL,NULL),(102,4,'','1726','17e','','','synthetic resin jacket crown*','synth resin jacket crown',6785,5428,0,0,0,NULL,NULL,NULL,NULL),(103,4,'','1700','','','','first crown/inlay extra fee','addnl for 1st crown in arch',785,628,0,0,0,NULL,NULL,NULL,NULL),(104,4,'','1731','','','Private only','precious metal core and post','pm alloy core & post',0,0,4800,6000,0,NULL,NULL,NULL,NULL),(105,4,'','1732','17f2','','','non-precious metal cast core and post','non-pm alloy core & post',3515,2812,0,0,0,NULL,NULL,NULL,NULL),(106,4,'','1733','17f3','','','non-precious metal core and post','prefab non-pm alloy core & post',1835,1468,4800,6000,0,NULL,NULL,NULL,NULL),(107,4,'','1734','17f4','','','crown/inlay pin/screw retainer*','pin/screw retention',875,700,1850,0,0,NULL,NULL,NULL,NULL),(108,4,'','1735','17f5','','','inlay facing*','facing for inlay',1020,816,0,0,0,NULL,NULL,NULL,NULL),(109,4,'','1736','','','','crown facing*','facing for crown',1425,1140,0,0,0,NULL,NULL,NULL,NULL),(110,4,'','1737','','','Private only','composite crown facing*','lab-processed composite facing',0,0,0,0,0,NULL,NULL,NULL,NULL),(111,4,'','1738','17f7','','','crown dovetail*','lab-produced dovetail/slot',1730,1384,0,0,0,NULL,NULL,NULL,NULL),(112,4,'','1739','17f8','','','crown milled edge*','parallel metallic sfce (crown)',1610,1288,0,0,0,NULL,NULL,NULL,NULL),(113,4,'','1742','17g','','','temporary crown*','temp crown, non post-retained',1465,1172,5500,6000,0,NULL,NULL,NULL,NULL),(114,4,'','1743','','','','post-retd temporary crown*','temp crown, post-retained',2065,1652,6380,9000,0,NULL,NULL,NULL,NULL),(115,4,'','1744','17h','','','removal of a post fractured at or below root face','removal of fractured post',1605,1284,0,0,0,NULL,NULL,NULL,NULL),(116,4,'','1751','17i','','discretionary','other type of crown*','other types of crown',0,0,0,0,0,NULL,NULL,NULL,NULL),(117,4,'','1761','17j1','','','inlay facing repair*','renewal of inlay facing',1020,816,4620,0,0,NULL,NULL,NULL,NULL),(118,4,'','1762','','','','crown facing repair*','renewal of crown facing',1200,960,4620,0,0,NULL,NULL,NULL,NULL),(119,4,'','1771','17j2','','discretionary','crown repair*','other crown repairs',0,0,0,0,0,NULL,NULL,NULL,NULL),(120,4,'','1781','17k','','','recementing inlay*','recementing inlay',1055,84,4600,0,0,NULL,NULL,NULL,NULL),(121,4,'','1782','','','','recementing crown*','recementing crown',1055,844,4600,0,0,NULL,NULL,NULL,NULL),(122,4,'','1801','18a1','','','compound inlay bridge retainer*','compound inlay retnr',10185,8148,28000,33000,0,NULL,NULL,NULL,NULL),(123,4,'','1802','','','','inlay or 3/4 crown bridge retainer*','comp conf inlay or 3/4 crown retnr',13070,10456,28000,33000,0,NULL,NULL,NULL,NULL),(124,4,'','1803','','','','full gold bridge retainer*','full gold crown retnr',13920,11136,28000,33000,0,NULL,NULL,NULL,NULL),(125,4,'','1804','18a2','','','precious metal bridge retainer*','pm alloy crown retnr',11945,9556,28000,33000,0,NULL,NULL,NULL,NULL),(126,4,'','1805','','','','non-precious metal bridge retainer*','non-pm alloy crown retnr',9335,7468,0,0,0,NULL,NULL,NULL,NULL),(127,4,'','1806','18a3','','','porcelain jacket bridge retainer*','porcelain jacket crown retnr',10185,8148,0,0,0,NULL,NULL,NULL,NULL),(128,4,'','1807','18a4','','','precious metal bonded bridge retainer*','gold/pm alloy bonded crown retnr',13385,10708,28000,33000,0,NULL,NULL,NULL,NULL),(129,4,'','1808','','','','non-precious metal bonded bridge retainer*','non-pm alloy bonded crown retnr',12205,9764,0,0,0,NULL,NULL,NULL,NULL),(130,4,'','1811','18b1','','','precious metal bridge core and post','pm alloy core & post',3620,2896,4800,6000,0,NULL,NULL,NULL,NULL),(131,4,'','1812','18b2','','','non-precious metal cast bridge core and post','non-pm core & post',2500,2000,0,0,0,NULL,NULL,NULL,NULL),(132,4,'','1813','18b3','','','non-precious metal bridge core and post','prefab non-pm alloy core & post',1835,1468,4800,6000,0,NULL,NULL,NULL,NULL),(133,4,'','1814','18b4','','','pin/screw bridge retainer*','pin/screw retention',875,700,1850,0,0,NULL,NULL,NULL,NULL),(134,4,'','1815','18b5','','discretionary','bridge dovetail*','dovetail',0,0,4180,0,0,NULL,NULL,NULL,NULL),(135,4,'','1816','18b6','','','bridge retainer composite facing*','comp facing retnr',2710,2168,0,0,0,NULL,NULL,NULL,NULL),(136,4,'','1821','18c1','','','gold bridge pontic*','60% + gold alloy pontic',6960,5568,28000,33000,0,NULL,NULL,NULL,NULL),(137,4,'','1822','18c2','','','precious metal bridge pontic*','pm alloy pontic',5060,4048,28000,33000,0,NULL,NULL,NULL,NULL),(138,4,'','1823','','','','non-precious metal bridge pontic*','non-pm alloy pontic',3570,2856,0,0,0,NULL,NULL,NULL,NULL),(139,4,'','1824','18c3','','','porcelain bridge pontic*','porcelain pontic',5085,4068,28000,33000,0,NULL,NULL,NULL,NULL),(140,4,'','1825','18c4','','','gold/precious metal bonded bridge pontic*','gold/pm bonded pontic',7605,6084,28000,33000,0,NULL,NULL,NULL,NULL),(141,4,'','1826','','','','non-precious metal bonded bridge pontic*','non-pm bonded pontic',6610,5288,0,0,0,NULL,NULL,NULL,NULL),(142,4,'','1827','18c5','','','bridge pontic composite facing*','comp facing pontic',2725,2180,0,0,0,NULL,NULL,NULL,NULL),(143,4,'','1831','18d1','','','cast metal bridge retainer*','cast metal retnr',3885,3108,28000,33000,0,NULL,NULL,NULL,NULL),(144,4,'','1832','18d2','','','bonded porcelain bridge pontic*','bonded porcelain pontic',7430,5944,28000,33000,0,NULL,NULL,NULL,NULL),(145,4,'','1841','18e','','discretionary','bridge unit*','any other type perm br unit',0,0,0,0,0,NULL,NULL,NULL,NULL),(146,4,'','1851','18f','','','type 1 temporary bridge unit*','temp bridge, >= 3 months (unit)',1730,1384,7865,8000,0,NULL,NULL,NULL,NULL),(147,4,'','1852','18f','','','type 2 temporary bridge unit*','temp bridge, < 3 months (unit)',645,516,7865,8000,0,NULL,NULL,NULL,NULL),(148,4,'','1861','18g1','','','recementing acid-etch bridge*','recementing acid-etch bridge',2885,0,8250,0,0,NULL,NULL,NULL,NULL),(149,4,'','1862','18g2','','','recementing bridge*','recementing any other bridge',1530,0,8250,0,0,NULL,NULL,NULL,NULL),(150,4,'','1871','18h','','discretionary','bridge repair*','repairing bridge',0,0,0,0,0,NULL,NULL,NULL,NULL),(151,5,'EX','2101','21','','','extraction*','extraction, 1 tooth',785,628,3050,0,0,NULL,NULL,NULL,NULL),(152,5,'','2101','','','','','extraction, 2 teeth',1425,1140,4015,4050,0,NULL,NULL,NULL,NULL),(153,5,'','2101','','','','','extraction, 3-4 teeth',2195,1756,5225,7000,0,NULL,NULL,NULL,NULL),(154,5,'','2101','','','','','extraction, 5-9 teeth',2885,2308,6655,7000,0,NULL,NULL,NULL,NULL),(155,5,'','2101','','','','','extraction, 10-16 teeth',3885,3108,8690,10000,0,NULL,NULL,NULL,NULL),(156,5,'','2101','','','','','extraction, > 16 teeth',4745,3796,10505,15000,0,NULL,NULL,NULL,NULL),(157,5,'','2121','','','','extraction visit*','extrns, fee per visit',645,516,1600,2000,0,NULL,NULL,NULL,NULL),(158,5,'','2201','22a1','','','type 1 surgical extraction*','surg extrn soft tissue',2195,1756,5225,0,0,NULL,NULL,NULL,NULL),(159,5,'','2202','22a2i','','','type 2a surgical extraction*','surg extrn bone removal, 1-3',3050,2440,8250,9000,0,NULL,NULL,NULL,NULL),(160,5,'','2203','22a2ii','','','type 2b surgical extraction*','surg extrn 4-8 except impacted 8s',3745,2996,8250,9000,0,NULL,NULL,NULL,NULL),(161,5,'','2204','22a2iii','','','type 3 (upper) surgical extraction*','surg extrn impacted 8s, no divn U',3885,3108,8250,9000,0,NULL,NULL,NULL,NULL),(162,5,'','2206','','','','type 3 (lower) surgical extraction*','surg extrn impacted 8s, no divn L',4590,3672,9460,0,0,NULL,NULL,NULL,NULL),(163,5,'','2205','22s2iv','','','type 4 (upper) surgical extraction*','surg extrn impacted 8s, divn U',4915,3932,10120,0,0,NULL,NULL,NULL,NULL),(164,5,'','2207','','','','type 4 (lower) surgical extraction*','surg extrn impacted 8s, divn L',5440,4352,11165,0,0,NULL,NULL,NULL,NULL),(165,5,'','2211','22b','','','fraenectomy^','fraenectomy (course)',3050,2440,6985,0,0,NULL,NULL,NULL,NULL),(166,5,'','2221','22c','','discretionary','type 5 surgical extraction*','other surgery/more complex ops',0,0,0,0,0,NULL,NULL,NULL,NULL),(167,5,'','2301','23a1','','','arrest of bleeding^','arrest of bleeding (visit)',2500,0,5390,0,0,NULL,NULL,NULL,NULL),(168,5,'','2302','23a2','','','removal of plugs/sutures^','removal plugs/sutures only (visit)',785,0,1705,0,0,NULL,NULL,NULL,NULL),(169,5,'','2311','23b','','','trtmt of infected sockets^','infected sockets (1 visit)',785,628,2145,2500,0,NULL,NULL,NULL,NULL),(170,5,'','2311','','','','','inf sockets > 1 visit',1610,1288,3465,0,0,NULL,NULL,NULL,NULL),(171,5,'','2551','25a1','','','sedation type 1A','sedn extrns 1-4 teeth',2500,2000,0,0,0,NULL,NULL,NULL,NULL),(172,5,'','2552','','','','sedation type 1B','sedn extrns 5-9 teeth',2885,2308,0,0,0,NULL,NULL,NULL,NULL),(173,5,'','2553','','','','sedation type 1C','sedn extrns 10-16 teeth',3395,2716,0,0,0,NULL,NULL,NULL,NULL),(174,5,'','2554','','','','sedation type 1D','sedn extrns 17+ teeth',4230,3384,0,0,0,NULL,NULL,NULL,NULL),(175,5,'','2560','','','','sedation for extractions^','sedn oth trt band D',8460,6768,0,0,0,NULL,NULL,NULL,NULL),(176,5,'','2555','25b2','','','sedation type 2A','sedn extrns max per course',8460,6768,0,0,0,NULL,NULL,NULL,NULL),(177,5,'','2556','','','','sedation type 2B','sedn oth trt band A',2500,2000,0,0,0,NULL,NULL,NULL,NULL),(178,5,'','2557','','','','sedation type 2C','sedn oth trt band B',4590,3672,0,0,0,NULL,NULL,NULL,NULL),(179,5,'','2558','','','','sedation type 2D','sedn oth trt band C',6610,5288,0,0,0,NULL,NULL,NULL,NULL),(180,5,'','2561','25a3','','discretionary','sedation type 3','(sedn oth trt cap)',0,0,0,0,0,NULL,NULL,NULL,NULL),(181,5,'','2563','25a4','','discretionary','sedation type 4','sedn veneers, crowns, inlays, bridges',0,0,0,0,0,NULL,NULL,NULL,NULL),(182,5,'','2566','25b','','','sedation attendance type 1','sedn anaesthetist call-out < 1 mile',2885,0,0,0,0,NULL,NULL,NULL,NULL),(183,5,'','2567','25b','','','sedation attendance type 2','sedn anaesthetist call-out >= 1 mile',5085,0,0,0,0,NULL,NULL,NULL,NULL),(184,5,'','2573','25c2','','','type 2 sedative by inhalation','inhalation',1200,960,0,0,0,NULL,NULL,NULL,NULL),(185,5,'','2573','','','','','inhalation supplement',570,0,0,0,0,NULL,NULL,NULL,NULL),(186,5,'','2574','25c2','','','type 2 sedative by injection','injection',2145,1716,0,0,0,NULL,NULL,NULL,NULL),(187,5,'','2574','','','','','injection supplement',740,0,0,0,0,NULL,NULL,NULL,NULL),(188,6,'','2701','27a1','','','occlusal additions^','occlusal build-up',1730,1384,6270,0,0,NULL,NULL,NULL,NULL),(189,6,'','2711','27a2','','','upper temporary base*','temporary base U/L (applicn)',2305,1844,0,0,0,NULL,NULL,NULL,NULL),(190,6,'','2712','27a2','','','lower temporary base*','temporary base U/L (applicn)',2305,1844,0,0,0,NULL,NULL,NULL,NULL),(191,6,'','2712','','','','','temp base max per course',4590,3672,0,0,0,NULL,NULL,NULL,NULL),(192,6,'','2721','27a3','','discretionary','preparatory trtmt for dentures^','other preparatory trtmt',0,0,0,0,0,NULL,NULL,NULL,NULL),(193,6,'','2730','27b1','','','full synthetic resin dentures^','sr f/f',17345,13876,56000,4464,0,NULL,NULL,NULL,NULL),(194,6,'','2731','27b2','','','full synthetic resin upper denture','sr full upper',10820,8656,37500,44500,0,NULL,NULL,NULL,NULL),(195,6,'','2732','27b2','','','full synthetic resin lower denture','sr full lower',10820,8656,37500,44500,0,NULL,NULL,NULL,NULL),(196,6,'','2733','27b3','','','partial upper synthetic resin denture','sr partial, 1-3 teeth',6785,5428,32000,0,0,NULL,NULL,NULL,NULL),(197,6,'','2733','','','','','ditto, 4-8 teeth',8990,7192,32000,38000,0,NULL,NULL,NULL,NULL),(198,6,'','2733','','','','','ditto, > 8 teeth',10695,8556,35000,38000,0,NULL,NULL,NULL,NULL),(199,6,'','2735','27b3','','','partial lower synthetic resin denture','sr partial, 1-3 teeth',6785,5428,32000,0,0,NULL,NULL,NULL,NULL),(200,6,'','2735','','','','','ditto, 4-8 teeth',8990,7192,32000,38000,0,NULL,NULL,NULL,NULL),(201,6,'','2735','','','','','ditto, > 8 teeth',10695,8556,35000,38000,0,NULL,NULL,NULL,NULL),(202,6,'','2735','','','','','max for any sr comb',20890,16712,5964,0,0,NULL,NULL,NULL,NULL),(203,6,'','2734','27b4','','','lingual/palatal bar*','addnl for lingual/palatal bar',1425,1140,3300,0,0,NULL,NULL,NULL,NULL),(204,6,'','2741','27c1','','','full metal upper denture','cc/ss full U',15285,1222,44000,47500,0,NULL,NULL,NULL,NULL),(205,6,'','2742','27c1','','','full metal lower denture','cc/ss full L',15285,1222,44000,47500,0,NULL,NULL,NULL,NULL),(206,6,'','2743','27c2','','','partial upper plate type metal denture','plate ptl, 1-3 teeth',15620,12496,49500,0,0,NULL,NULL,NULL,NULL),(207,6,'','2743','','','','','ditto 4-8 teeth',17135,13708,49500,0,0,NULL,NULL,NULL,NULL),(208,6,'','2743','','','','','ditto > 8 teeth',17815,14252,49500,0,0,NULL,NULL,NULL,NULL),(209,6,'','2747','27c2','','','partial lower plate type metal denture','plate ptl, 1-3 teeth',15620,12496,49500,0,0,NULL,NULL,NULL,NULL),(210,6,'','2747','','','','','ditto 4-8 teeth',17135,13708,49500,0,0,NULL,NULL,NULL,NULL),(211,6,'','2747','','','','','ditto > 8 teeth',17815,14252,49500,0,0,NULL,NULL,NULL,NULL),(212,6,'','2744','27c3','','','partial upper skel type metal denture','skelet ptl, 1 conn bar, 1-3 teeth',16465,13172,49500,0,0,NULL,NULL,NULL,NULL),(213,6,'','2744','','','','','ditto, > 3 teeth',17980,14384,49500,0,0,NULL,NULL,NULL,NULL),(214,6,'','2748','27c3','','','partial lower skel type metal denture','skelet ptl, 1 conn bar, 1-3 teeth',16465,13172,49500,0,0,NULL,NULL,NULL,NULL),(215,6,'','2748','','','','','ditto, > 3 teeth',17980,14384,49500,0,0,NULL,NULL,NULL,NULL),(216,6,'','2745','27c4','','','partial upper skel multiple connectors metal denture','skelet ptl, > 1 conn bar, 1-3 teeth',17135,13708,49500,0,0,NULL,NULL,NULL,NULL),(217,6,'','2745','','','','','ditto, > 3 teeth',19185,15348,49500,0,0,NULL,NULL,NULL,NULL),(218,6,'','2749','27c4','','','partial lower skel multiple connectors metal denture','skelet ptl, > 1 conn bar, 1-3 teeth',17135,13708,49500,0,0,NULL,NULL,NULL,NULL),(219,6,'','2749','','','','','ditto, > 3 teeth',19185,15348,49500,0,0,NULL,NULL,NULL,NULL),(220,6,'','2746','27c5','','','backing for denture teeth','addnl for backing per tooth',1080,864,0,0,0,NULL,NULL,NULL,NULL),(221,6,'','2746','','','','','max for backing per denture',6450,5160,0,0,0,NULL,NULL,NULL,NULL),(222,6,'','2751','27c6','','discretionary','metal denture*','other metal dentures',0,0,0,0,0,NULL,NULL,NULL,NULL),(223,6,'','2761','27d','','','soft lining (upper)','addnl for soft lining',3570,2856,4400,0,0,NULL,NULL,NULL,NULL),(224,6,'','2762','27d','','','soft lining (lower)','addnl for soft lining',3570,2856,4400,0,0,NULL,NULL,NULL,NULL),(225,6,'','2771','27e','','','special tray (upper)','special tray',1730,1384,5280,0,0,NULL,NULL,NULL,NULL),(226,6,'','2772','27e','','','special tray (lower)','special tray',1730,1384,5280,0,0,NULL,NULL,NULL,NULL),(227,6,'','2781','27f','','','metal strip id insert (upper)','metal strip id',550,440,1375,0,0,NULL,NULL,NULL,NULL),(228,6,'','2782','27f','','','metal strip id insert (lower)','metal strip id',550,440,1375,0,0,NULL,NULL,NULL,NULL),(229,6,'','2738','','','','max fee for resin dentures','max for any sr comb',20890,16712,5964,0,0,NULL,NULL,NULL,NULL),(230,6,'','2801','28a1','','','upper denture general repair*','gen repairs, 1 repair',1635,0,5060,0,0,NULL,NULL,NULL,NULL),(231,6,'','2801','','','','','each addnl repair',570,0,1980,0,0,NULL,NULL,NULL,NULL),(232,6,'','2802','28a1','','','lower denture general repair*','gen repairs, 1 repair',1635,0,5060,0,0,NULL,NULL,NULL,NULL),(233,6,'','2802','','','','','each addnl repair',570,0,1980,0,0,NULL,NULL,NULL,NULL),(234,6,'','2803','28a2','','','upper denture clasp repair*','clasp repairs, 1 repair',2375,0,5115,0,0,NULL,NULL,NULL,NULL),(235,6,'','2803','','','','','each addnl repair',1150,0,2530,0,0,NULL,NULL,NULL,NULL),(236,6,'','2804','28a2','','','lower denture clasp repair*','clasp repairs, 1 repair',2375,0,5115,0,0,NULL,NULL,NULL,NULL),(237,6,'','2804','','','','','each addnl repair',1150,0,2530,0,0,NULL,NULL,NULL,NULL),(238,6,'','2811','28a3','','discretionary','metal denture repairs^','other repairs (metal)',0,0,7645,0,0,NULL,NULL,NULL,NULL),(239,6,'','2821','28a4','','','upper denture impression^','addnl impression technique',755,0,2310,0,0,NULL,NULL,NULL,NULL),(240,6,'','2822','28a4','','','lower denture impression^','addnl impression technique',755,0,2310,0,0,NULL,NULL,NULL,NULL),(241,6,'','2822','','','','','2nd repair',570,0,1155,0,0,NULL,NULL,NULL,NULL),(242,6,'','2810','28','','','upper denture repairs^','max repairs per denture',3745,0,8910,0,0,NULL,NULL,NULL,NULL),(243,6,'','2820','28','','','lower denture repairs^','max repairs per denture',3745,0,8910,0,0,NULL,NULL,NULL,NULL),(244,6,'','2831','28b1','','','denture adjustments (upper)','adjustments',1150,920,3520,0,0,NULL,NULL,NULL,NULL),(245,6,'','2832','28b1','','','denture adjustments (lower)','adjustments',1150,920,3520,0,0,NULL,NULL,NULL,NULL),(246,6,'','2841','28b2','','discretionary','metal denture adjustments','other adjustments (metal)',0,0,0,0,0,NULL,NULL,NULL,NULL),(247,6,'','2851','28c1','','','upper denture reline/rebase','reline/rebase',3885,3108,10780,0,0,NULL,NULL,NULL,NULL),(248,6,'','2852','28c1','','','lower denture reline/rebase','reline/rebase',3885,3108,10780,0,0,NULL,NULL,NULL,NULL),(249,6,'','2853','28c2','','','upper denture reline with flange','ditto plus labial/buccal flange',4415,3532,10780,0,0,NULL,NULL,NULL,NULL),(250,6,'','2854','28c2','','','lower denture reline with flange','ditto plus labial/buccal flange',4415,3532,10780,0,0,NULL,NULL,NULL,NULL),(251,6,'','2855','28c3','','','soft lining (upper)','soft lining',5955,4764,10780,0,0,NULL,NULL,NULL,NULL),(252,6,'','2856','28c3','','','soft lining (lower)','soft lining',5955,4764,10780,0,0,NULL,NULL,NULL,NULL),(253,6,'','2861','28d1','','','upper denture addition of clasp*','addition of clasp',3220,2576,6985,0,0,NULL,NULL,NULL,NULL),(254,6,'','2862','28d1','','','lower denture addition of clasp*','addition of clasp',3220,2576,6985,0,0,NULL,NULL,NULL,NULL),(255,6,'','2863','28d2','','','addition of teeth to upper denture','addition of tooth',2710,2168,6985,0,0,NULL,NULL,NULL,NULL),(256,6,'','2864','28d2','','','addition of teeth to lower denture','addition of tooth',2710,2168,6985,0,0,NULL,NULL,NULL,NULL),(257,6,'','2865','28d3','','','upper denture addition of gum','addition of gum',2710,2168,5885,0,0,NULL,NULL,NULL,NULL),(258,6,'','2866','28d3','','','lower denture addition of gum','addition of gum',2710,2168,5885,0,0,NULL,NULL,NULL,NULL),(259,6,'','2871','28d4','','discretionary','metal denture additions','other additions (metal)',0,0,0,0,0,NULL,NULL,NULL,NULL),(260,6,'','2871','','','','','max reps & addns per denture',4590,3672,13200,0,0,NULL,NULL,NULL,NULL),(261,6,'','2901','29a','','discretionary','obturator(s)^','obturators (case)',0,0,0,0,0,NULL,NULL,NULL,NULL),(262,6,'','2911','29b','','discretionary','obturator repair*','obturator repairs',0,0,0,0,0,NULL,NULL,NULL,NULL),(263,6,'','2921','29c1','','','foil splint*','foil splint',2375,1900,6985,0,0,NULL,NULL,NULL,NULL),(264,6,'','2922','29c2','','','composite splint union*','composite splint (per union)',1730,1384,3740,0,0,NULL,NULL,NULL,NULL),(265,6,'','2922','','','','','comp splint max per arch',6285,5028,12925,0,0,NULL,NULL,NULL,NULL),(266,6,'','2923','29c3','','','composite splint insert*','addnl for bar or wire',365,292,1375,0,0,NULL,NULL,NULL,NULL),(267,6,'','2924','29c4','','','acrylic splint unit*','acrylic splint (per unit)',2030,1624,4400,0,0,NULL,NULL,NULL,NULL),(268,6,'','2924','','','','','max',7125,5700,15400,0,0,NULL,NULL,NULL,NULL),(269,6,'','2925','29c5','','','cast metal splint unit*','cast metal splint (per unit)',4415,3532,9515,0,0,NULL,NULL,NULL,NULL),(270,6,'','2925','','','','','max',15445,12356,33275,0,0,NULL,NULL,NULL,NULL),(271,6,'','2926','29c6','','discretionary','splint*','any other type splint',0,0,0,0,0,NULL,NULL,NULL,NULL),(272,6,'','2941','29d','','','dental appliance*','acrylic occlusal appl',8315,6652,17930,0,0,NULL,NULL,NULL,NULL),(273,6,'','2991','29e','','discretionary','occlusal appliance*','other appliances',0,0,0,0,0,NULL,NULL,NULL,NULL),(274,7,'','3241','32c1','','','upper removable appliance acrylic repair','acryl rep, remov appl U',2500,0,0,0,0,NULL,NULL,NULL,NULL),(275,7,'','3247','32c1','','','lower removable appliance acrylic repair','acryl rep, remov appl L',2500,0,0,0,0,NULL,NULL,NULL,NULL),(276,7,'','3242','32c2','','','upper removable appliance metal repair*','metal rep, remov appl',3050,0,0,0,0,NULL,NULL,NULL,NULL),(277,7,'','3248','32c2','','','lower removable appliance metal repair*','metal rep, remov appl',3050,0,0,0,0,NULL,NULL,NULL,NULL),(278,7,'','3248','','','','','second metal rep',785,0,0,0,0,NULL,NULL,NULL,NULL),(279,7,'','3248','','','','','2nd combined ortho rep',785,0,0,0,0,NULL,NULL,NULL,NULL),(280,7,'','3248','','','','','max for combined ortho reps',3910,0,0,0,0,NULL,NULL,NULL,NULL),(281,7,'','3243','32c3','','','functional appliance repair*','functnl appl rep',3885,0,0,0,0,NULL,NULL,NULL,NULL),(282,7,'','3244','32c4','','','upper fixed appliance repair*','fixed appl rep',5265,0,0,0,0,NULL,NULL,NULL,NULL),(283,7,'','3249','32c4','','','lower fixed appliance metal repair*','fixed appl rep',5265,0,0,0,0,NULL,NULL,NULL,NULL),(284,7,'','3245','32c','','','upper orthodontic repair impression*','impression',755,0,0,0,0,NULL,NULL,NULL,NULL),(285,7,'','3246','32c','','','lower orthodontic repair impression*','impression',755,0,0,0,0,NULL,NULL,NULL,NULL),(286,7,'','3261','32d1','','','upper fixed appliance tooth addition*','ortho fixed appl 1st tooth added (U)',1315,1052,0,0,0,NULL,NULL,NULL,NULL),(287,7,'','3261','','','','','further teeth added per tooth',1315,1052,0,0,0,NULL,NULL,NULL,NULL),(288,7,'','3262','32d1','','','lower fixed appliance tooth addition*','ortho fixed appl 1st tooth added (L)',1315,1052,0,0,0,NULL,NULL,NULL,NULL),(289,7,'','3262','','','','','further teeth added per tooth',1315,1052,0,0,0,NULL,NULL,NULL,NULL),(290,7,'','3262','','','','','ortho fixed appl tooth addns max per app',2630,2104,0,0,0,NULL,NULL,NULL,NULL),(291,7,'','3263','32d2','','','upper removable appliance tooth addition*','ortho remov appl 1st tooth added (U)',1955,1564,0,0,0,NULL,NULL,NULL,NULL),(292,7,'','3263','','','','','further teeth added per tooth',1955,1564,0,0,0,NULL,NULL,NULL,NULL),(293,7,'','3264','32d2','','','lower removable appliance tooth addition*','ortho remov appl 1st tooth added (L)',1955,1564,0,0,0,NULL,NULL,NULL,NULL),(294,7,'','3264','','','','','further teeth added per tooth',1955,1564,0,0,0,NULL,NULL,NULL,NULL),(295,7,'','3264','','','','','ortho remov appl tooth addns max per app',3910,3128,0,0,0,NULL,NULL,NULL,NULL),(296,7,'','3281','32e1','','','space maintainer/retention appliance*','sm/ret appl',4745,3796,10230,0,0,NULL,NULL,NULL,NULL),(297,7,'','3282','32e2','','','removable spring/screw appliance*','removable spr/scr appl',6450,5160,13915,0,0,NULL,NULL,NULL,NULL),(298,7,'','3283','32e3','','','simple fixed appliance*','simple fixed appl',6610,5288,14245,0,0,NULL,NULL,NULL,NULL),(299,7,'','3284','32e4','','','multiband/bracket appliance*','fixed multib appl',12390,9912,26730,0,0,NULL,NULL,NULL,NULL),(300,7,'','3285','32e5','','','functional appliance*','functional appl',7640,6112,16445,0,0,NULL,NULL,NULL,NULL),(301,7,'','3291','','','discretionary','other ortho adj/rep','other ortho adj/rep',0,0,0,0,0,NULL,NULL,NULL,NULL),(302,8,'','3501','35a','','','domiciliary visit* <10 miles','domiciliary visits, < 10 miles',3570,0,7700,0,0,NULL,NULL,NULL,NULL),(303,8,'','3502','35a','','','domiciliary visit* 10-40 miles','ditto, 10-40 miles',4915,0,10615,0,0,NULL,NULL,NULL,NULL),(304,8,'','3503','','','','domiciliary visit* >40 miles','ditto, > 40 miles',6450,0,13970,0,0,NULL,NULL,NULL,NULL),(305,8,'','3511','','','','recalled attendance*  <1 mile','recalled attendance, < 1 mile',4230,0,7500,0,0,NULL,NULL,NULL,NULL),(306,8,'','3512','35b','','','recalled attendance*  >=1mile','ditto, >= 1 mile',6960,0,7500,0,0,NULL,NULL,NULL,NULL),(307,8,'','3601','','','','taking material for lab examination^','matl for path/bact exam (course)',1200,960,2585,0,0,NULL,NULL,NULL,NULL),(308,8,'','3611','36a','','','stoning/smoothing teeth','stoning, 1 tooth',280,224,660,0,0,NULL,NULL,NULL,NULL),(309,8,'','3611','36b','','','','ditto, > 1 tooth',520,416,1100,0,0,NULL,NULL,NULL,NULL),(310,8,'','3621','36c','','discretionary','occlusal equilibration^','occlusal equilibration',0,0,0,0,0,NULL,NULL,NULL,NULL),(311,8,'','3631','36d','','','trtmt for sensitive cementum/dentine^','sensitive cementum',520,416,1045,0,0,NULL,NULL,NULL,NULL),(312,8,'','3641','36e','','','issue of prescription*','prescription',435,348,600,0,0,NULL,NULL,NULL,NULL),(313,8,'','3651','36f','','','tooth reimplantation*','reimplantation of tooth',1635,1308,0,0,0,NULL,NULL,NULL,NULL),(314,8,'','3661','36g','','','removal of fractured crown*','removal fractured crown',825,660,2750,0,0,NULL,NULL,NULL,NULL),(315,8,'','3671','36h','','','overdenture preparation^','removal corona',1110,888,2420,0,0,NULL,NULL,NULL,NULL),(316,8,'','3701','37','','','trtmt for acute conditions^','trtmt for acute conds',755,604,2750,3500,0,NULL,NULL,NULL,NULL),(317,8,'','4001','40','','discretionary','other treatment^','any other trtmt',0,0,0,0,0,NULL,NULL,NULL,NULL),(318,9,'','4401','44a','','','deciduous filling','deciduous filling',785,0,0,0,0,NULL,NULL,NULL,NULL),(319,9,'','4402','44b','','','stainless steel crown','stainless steel crown',2065,0,0,0,0,NULL,NULL,NULL,NULL),(320,9,'','4403','44c','','','deciduous pulpotomy','deciduous pulpotomy',825,0,0,0,0,NULL,NULL,NULL,NULL),(321,9,'','4404','44d','','','deciduous pulpectomy','deciduous pulpectomy',1570,0,0,0,0,NULL,NULL,NULL,NULL),(322,9,'','4405','44e','','','deciduous filling on referral','deciduous filling on referral',1395,0,0,0,0,NULL,NULL,NULL,NULL),(323,9,'','4406','44f','','','preventive fissure sealant*','preventive fissure sealants (tooth)',785,0,0,0,0,NULL,NULL,NULL,NULL),(324,12,'','4701','47a','','1','clinical assessment^','clinical assessment',800,0,0,0,0,NULL,NULL,NULL,NULL),(325,12,'','4801','48','','','issue of prescription*','prescription',435,348,0,0,0,NULL,NULL,NULL,NULL),(326,12,'','4901','49a','','1','small xray*','small xrays 1 film',395,316,0,0,0,NULL,NULL,NULL,NULL),(327,12,'','4901','','','2','','small xrays 2 films',550,440,0,0,0,NULL,NULL,NULL,NULL),(328,12,'','4901','','','3','','small xrays 3 films',675,540,0,0,0,NULL,NULL,NULL,NULL),(329,12,'','4901','','','ADDITIONAL','','small xrays each addnl',180,144,0,0,0,NULL,NULL,NULL,NULL),(330,12,'','4901','','','MAX','','small xrays max for addnl',1630,1304,0,0,0,NULL,NULL,NULL,NULL),(331,12,'','4911','49b','','1','medium xray*','medium xrays 1 film',520,416,0,0,0,NULL,NULL,NULL,NULL),(332,12,'','4911','','','ADDITIONAL','','medium xrays each addnl',225,180,0,0,0,NULL,NULL,NULL,NULL),(333,12,'','4911','','','MAX','','medium xrays max for addnl',465,372,0,0,0,NULL,NULL,NULL,NULL),(334,12,'','4921','49c','','1','large xray*','large xrays 1 film',825,660,0,0,0,NULL,NULL,NULL,NULL),(335,12,'','4921','','','ADDITIONAL','','large xrays each addnl',395,316,0,0,0,NULL,NULL,NULL,NULL),(336,12,'','4921','','','MAX','','large xrays max for addnl',785,628,0,0,0,NULL,NULL,NULL,NULL),(337,12,'','4931','49d','','1','panoral xray*','panoral xray',1225,980,0,0,0,NULL,NULL,NULL,NULL),(338,12,'','5001','50a','','1','dressing*','dressing',600,480,0,0,0,NULL,NULL,NULL,NULL),(339,12,'','5001','','','2','','',855,684,0,0,0,NULL,NULL,NULL,NULL),(340,12,'','5001','','','ADDITIONAL','','',225,180,0,0,0,NULL,NULL,NULL,NULL),(341,12,'','5001','','','MAX','','',1775,1420,0,0,0,NULL,NULL,NULL,NULL),(342,12,'','5011','50b','','','incising an abscess','incising an abscess (per abscess)',785,628,0,0,0,NULL,NULL,NULL,NULL),(343,12,'','5021','50c','','','opening root canals for drainage','opening root canals for drainage',900,720,0,0,0,NULL,NULL,NULL,NULL),(344,12,'PX','5031','50d','','','pulp extirpation single root','pulp extirpation and dressing',1260,1008,0,0,0,NULL,NULL,NULL,NULL),(345,12,'PX+','5032','50d','','','pulp extirpation multi root','pulp extirpation multi root',1885,1508,0,0,0,NULL,NULL,NULL,NULL),(346,12,'ST','5041','50e','','','stoning/smoothing teeth','stoning, 1 tooth',280,224,0,0,0,NULL,NULL,NULL,NULL),(347,12,'','5041','','','','','ditto, > 1 tooth',520,416,0,0,0,NULL,NULL,NULL,NULL),(348,12,'','5051','50f','','','trtmt for sensitive cementum/dentine^','sensitive cementum',520,416,0,0,0,NULL,NULL,NULL,NULL),(349,12,'','5061','50g1','','','foil splint*','foil splint',2375,1900,0,0,0,NULL,NULL,NULL,NULL),(350,12,'','5062','50g2','','','composite splint union*','composite splint (per union)',1730,1384,0,0,0,NULL,NULL,NULL,NULL),(351,12,'','5062','','','','','comp splint max per arch',6285,5028,0,0,0,NULL,NULL,NULL,NULL),(352,12,'','5063','50g3','','','composite splint insert*','addnl for bar or wire',365,292,0,0,0,NULL,NULL,NULL,NULL),(353,12,'','5071','50h','','','tooth reimplantation*','reimplantation of tooth',1635,1308,0,0,0,NULL,NULL,NULL,NULL),(354,12,'','5075','50i','','','removal of fractured crown*','removal fractured crown',825,660,0,0,0,NULL,NULL,NULL,NULL),(355,12,'','5102','51a','','','temporary crown*','temp crown, non post-retained',1465,1172,0,0,0,NULL,NULL,NULL,NULL),(356,12,'','5103','51a','','','post-retd temporary crown*','temp crown, post-retained',2065,1652,0,0,0,NULL,NULL,NULL,NULL),(357,12,'','5104','51b','','','removal of a post fractured at or below root face','removal of fractured post',1605,1284,0,0,0,NULL,NULL,NULL,NULL),(358,12,'','5111','51c','','','recementing inlay*','recementing inlay',1055,844,0,0,0,NULL,NULL,NULL,NULL),(359,12,'','5112','51c','','','recementing crown*','recementing crown',1055,844,0,0,0,NULL,NULL,NULL,NULL),(360,12,'','5121','51c1','','','recementing acid-etch bridge*','recementing acid-etch bridge',2885,0,0,0,0,NULL,NULL,NULL,NULL),(361,12,'','5122','51c2','','','recementing bridge*','recementing any other bridge',1530,0,0,0,0,NULL,NULL,NULL,NULL),(362,12,'','5131','51d','','discretionary Fee','bridge repair*','repairing bridge',0,0,0,0,0,NULL,NULL,NULL,NULL),(363,12,'','5201','52a','','','extraction*','extraction, 1 tooth',785,628,0,0,0,NULL,NULL,NULL,NULL),(364,12,'','5201','','','','','extraction, 2 teeth',1425,1140,0,0,0,NULL,NULL,NULL,NULL),(365,12,'','5201','','','','','extraction, 3-4 teeth',2195,1756,0,0,0,NULL,NULL,NULL,NULL),(366,12,'','5201','','','','','extraction, 5-9 teeth',2885,2308,0,0,0,NULL,NULL,NULL,NULL),(367,12,'','5201','','','','','extraction, 10-16 teeth',3885,3108,0,0,0,NULL,NULL,NULL,NULL),(368,12,'','5201','','','','','extraction, > 16 teeth',4745,3796,0,0,0,NULL,NULL,NULL,NULL),(369,12,'','5206','','','','extraction visit*','extrns, fee per visit',645,516,0,0,0,NULL,NULL,NULL,NULL),(370,12,'','5211','52c1','','','type 1 surgical extraction*','surg extrn soft tissue',2195,1756,0,0,0,NULL,NULL,NULL,NULL),(371,12,'','5212','52c2','','','type 2a surgical extraction*','surg extrn bone removal, 1-3',3050,2440,0,0,0,NULL,NULL,NULL,NULL),(372,12,'','5213','','','','type 2b surgical extraction*','surg extrn 4-8 except impacted 8s',3745,2996,0,0,0,NULL,NULL,NULL,NULL),(373,12,'','5214','52c','','','type 3 (upper) surgical extraction*','surg extrn impacted 8s, no divn U',3885,3108,0,0,0,NULL,NULL,NULL,NULL),(374,12,'','5216','','','','type 3 (lower) surgical extraction*','surg extrn impacted 8s, no divn L',4590,3672,0,0,0,NULL,NULL,NULL,NULL),(375,12,'','5215','','','','type 4 (upper) surgical extraction*','surg extrn impacted 8s, divn U',4915,3932,0,0,0,NULL,NULL,NULL,NULL),(376,12,'','5217','','','','type 4 (lower) surgical extraction*','surg extrn impacted 8s, divn L',5440,4352,0,0,0,NULL,NULL,NULL,NULL),(377,12,'','5301','53a1','','','arrest of bleeding^','arrest of bleeding (visit)',2500,0,0,0,0,NULL,NULL,NULL,NULL),(378,12,'','5302','53a2','','','removal of plugs/sutures^','removal plugs/sutures only (visit)',785,0,0,0,0,NULL,NULL,NULL,NULL),(379,12,'','5311','53b','','','trtmt of infected sockets^','infected sockets (1 visit)',785,628,0,0,0,NULL,NULL,NULL,NULL),(380,12,'','5311','','','','','inf sockets > 1 visit',1610,1288,0,0,0,NULL,NULL,NULL,NULL),(381,12,'','5451','54b1','','','sedation type 1A','sedn extrns 1-4 teeth',2500,2000,0,0,0,NULL,NULL,NULL,NULL),(382,12,'','5452','','','','sedation type 1B','sedn extrns 5-9 teeth',2885,2308,0,0,0,NULL,NULL,NULL,NULL),(383,12,'','5453','','','','sedation type 1C','sedn extrns 10-16 teeth',3395,2716,0,0,0,NULL,NULL,NULL,NULL),(384,12,'','5454','','','','sedation type 1D','sedn extrns 17+ teeth',4230,3384,0,0,0,NULL,NULL,NULL,NULL),(385,12,'','5460','','','','sedation for extractions^','sedn oth trt band D',8460,6768,0,0,0,NULL,NULL,NULL,NULL),(386,12,'','5455','54b2','','','sedation type 2A','sedn extrns max per course',8460,2000,0,0,0,NULL,NULL,NULL,NULL),(387,12,'','5456','54b2','','','sedation type 2B','sedn oth trt band A',2500,3672,0,0,0,NULL,NULL,NULL,NULL),(388,12,'','5457','54b2','','','sedation type 2C','sedn oth trt band B',4590,5288,0,0,0,NULL,NULL,NULL,NULL),(389,12,'','5458','54b2','','','sedation type 2D','sedn oth trt band C',6610,6768,0,0,0,NULL,NULL,NULL,NULL),(390,12,'','5466','54b3','','','sedation attendance type 1','sedn anaesthetist call-out < 1 mile',2885,0,0,0,0,NULL,NULL,NULL,NULL),(391,12,'','5467','54b3','','','sedation attendance type 2','sedn anaesthetist call-out >= 1 mile',5085,0,0,0,0,NULL,NULL,NULL,NULL),(392,12,'','5473','','','','type 2 sedative by inhalation','inhalation',1200,960,0,0,0,NULL,NULL,NULL,NULL),(393,12,'','5473','','','','','inhalation supplement',570,0,0,0,0,NULL,NULL,NULL,NULL),(394,12,'','5474','','','','type 2 sedative by injection','injection',2145,1716,0,0,0,NULL,NULL,NULL,NULL),(395,12,'','5474','','','','','injection supplement',740,0,0,0,0,NULL,NULL,NULL,NULL),(396,12,'','5501','55a1','','','upper denture general repair*','gen repairs, 1 repair',1635,0,0,0,0,NULL,NULL,NULL,NULL),(397,12,'','5501','','','','','each addnl repair',570,0,0,0,0,NULL,NULL,NULL,NULL),(398,12,'','5502','55a1','','','lower denture general repair*','gen repairs, 1 repair',1635,0,0,0,0,NULL,NULL,NULL,NULL),(399,12,'','5502','','','','','each addnl repair',570,0,0,0,0,NULL,NULL,NULL,NULL),(400,12,'','5503','55a2','','','upper denture clasp repair*','clasp repairs, 1 repair',2375,0,0,0,0,NULL,NULL,NULL,NULL),(401,12,'','5503','','','','','each addnl repair',1150,0,0,0,0,NULL,NULL,NULL,NULL),(402,12,'','5504','55a2','','','lower denture clasp repair*','clasp repairs, 1 repair',2375,0,0,0,0,NULL,NULL,NULL,NULL),(403,12,'','5504','','','','','each addnl repair',1150,0,0,0,0,NULL,NULL,NULL,NULL),(404,12,'','5511','55a3','','discretionary','metal denture repairs^','other repairs (metal)',0,0,0,0,0,NULL,NULL,NULL,NULL),(405,12,'','5521','55a4','','','upper denture impression^','addnl impression technique',755,0,0,0,0,NULL,NULL,NULL,NULL),(406,12,'','5522','55a4','','','lower denture impression^','addnl impression technique',755,0,0,0,0,NULL,NULL,NULL,NULL),(407,12,'','5522','55','','','upper denture repairs^','max repairs per denture',3745,0,0,0,0,NULL,NULL,NULL,NULL),(408,12,'','5522','55','','','lower denture repairs^','max repairs per denture',3745,0,0,0,0,NULL,NULL,NULL,NULL),(409,12,'','5531','55b1','','','denture adjustments (upper)','adjustments',1150,920,0,0,0,NULL,NULL,NULL,NULL),(410,12,'','5532','55b1','','','denture adjustments (lower)','adjustments',1150,920,0,0,0,NULL,NULL,NULL,NULL),(411,12,'','5541','55b2','','discretionary','metal denture adjustments','other adjustments (metal)',0,0,0,0,0,NULL,NULL,NULL,NULL),(412,12,'','5551','55c1','','','upper denture reline/rebase','reline/rebase',3885,3108,0,0,0,NULL,NULL,NULL,NULL),(413,12,'','5552','55c1','','','lower denture reline/rebase','reline/rebase',3885,3532,0,0,0,NULL,NULL,NULL,NULL),(414,12,'','5553','55c2','','','upper denture reline with flange','ditto plus labial/buccal flange',4415,3532,0,0,0,NULL,NULL,NULL,NULL),(415,12,'','5554','55c2','','','lower denture reline with flange','ditto plus labial/buccal flange',4415,3532,0,0,0,NULL,NULL,NULL,NULL),(416,12,'','5555','55c3','','','soft lining (upper)','soft lining',5955,4764,0,0,0,NULL,NULL,NULL,NULL),(417,12,'','5556','55c3','','','soft lining (lower)','soft lining',5955,2576,0,0,0,NULL,NULL,NULL,NULL),(418,12,'','5561','55d1','','','upper denture addition of clasp*','addition of clasp',3220,2576,0,0,0,NULL,NULL,NULL,NULL),(419,12,'','5562','55d1','','','lower denture addition of clasp*','addition of clasp',3220,2576,0,0,0,NULL,NULL,NULL,NULL),(420,12,'','5563','55d2','','','addition of teeth to upper denture','addition of tooth',2710,2168,0,0,0,NULL,NULL,NULL,NULL),(421,12,'','5564','55d2','','','addition of teeth to lower denture','addition of tooth',2710,2168,0,0,0,NULL,NULL,NULL,NULL),(422,12,'','5565','55d3','','','upper denture addition of gum','addition of gum',2710,2168,0,0,0,NULL,NULL,NULL,NULL),(423,12,'','5566','55d3','','','lower denture addition of gum','addition of gum',2710,2168,0,0,0,NULL,NULL,NULL,NULL),(424,12,'','5571','55d4','','discretionary','metal denture additions','other additions (metal)',0,0,0,0,0,NULL,NULL,NULL,NULL),(425,12,'','5571','55','','','','max reps & addns per denture',4590,2168,0,0,0,NULL,NULL,NULL,NULL),(426,12,'','5581','55e2','','','upper removable appliance acrylic repair','acryl rep, remov appl U',2500,0,0,0,0,NULL,NULL,NULL,NULL),(427,12,'','5587','55e2','','','lower removable appliance acrylic repair','acryl rep, remov appl L',2500,0,0,0,0,NULL,NULL,NULL,NULL),(428,12,'','5582','55e3','','','upper removable appliance metal repair*','metal rep, remov appl',3050,0,0,0,0,NULL,NULL,NULL,NULL),(429,12,'','5588','55e3','','','lower removable appliance metal repair*','metal rep, remov appl',3050,0,0,0,0,NULL,NULL,NULL,NULL),(430,12,'','5588','','','','','second metal rep',785,0,0,0,0,NULL,NULL,NULL,NULL),(431,12,'','5588','','','','','2nd combined ortho rep',785,0,0,0,0,NULL,NULL,NULL,NULL),(432,12,'','5588','','','','','max for combined ortho reps',3910,0,0,0,0,NULL,NULL,NULL,NULL),(433,12,'','5583','55e4','','','functional appliance repair*','functnl appl rep',3885,0,0,0,0,NULL,NULL,NULL,NULL),(434,12,'','5584','55e5','','','upper fixed appliance repair*','fixed appl rep',5265,0,0,0,0,NULL,NULL,NULL,NULL),(435,12,'','5589','55e5','','','lower fixed appliance metal repair*','fixed appl rep',5265,0,0,0,0,NULL,NULL,NULL,NULL),(436,12,'','5585','55e','','','upper orthodontic repair impression*','impression',755,0,0,0,0,NULL,NULL,NULL,NULL),(437,12,'','5586','55e','','','lower orthodontic repair impression*','impression',755,0,0,0,0,NULL,NULL,NULL,NULL),(438,12,'','5601','56','','','trtmt for acute conditions^','trtmt for acute conds',755,604,0,0,0,NULL,NULL,NULL,NULL),(439,12,'','5701','57a','','','domiciliary visit* <10 miles','domiciliary visits, < 10 miles',3570,0,0,0,0,NULL,NULL,NULL,NULL),(440,12,'','5702','57a','','','domiciliary visit* 10-40 miles','ditto, 10-40 miles',4915,0,0,0,0,NULL,NULL,NULL,NULL),(441,12,'','5703','57a','','','domiciliary visit* >40 miles','ditto, > 40 miles',6450,0,0,0,0,NULL,NULL,NULL,NULL),(442,12,'','5711','57b','','','recalled attendance*  <1 mile','recalled attendance, < 1 mile',4230,0,0,0,0,NULL,NULL,NULL,NULL),(443,12,'','5712','57b','','','recalled attendance*  >=1mile','ditto, >= 1 mile',6960,0,0,0,0,NULL,NULL,NULL,NULL),(444,12,'','5811','58b1','','','single surface amalgam filling*','amalgam 1 sfce',855,684,0,0,0,NULL,NULL,NULL,NULL),(445,12,'','5812','58b2','','','compound amalgam filling*','amalgam > 1 sfce',1260,1008,0,0,0,NULL,NULL,NULL,NULL),(446,12,'','5813','58b3','','','mo/do amalgam filling*','amalgam > 1 sfce incl MO/DO',1660,1328,0,0,0,NULL,NULL,NULL,NULL),(447,12,'','5814','58b4','','','mod amalgam filling*','amalgam > 2 sfce incl MOD',2195,1756,0,0,0,NULL,NULL,NULL,NULL),(448,12,'','5814','','','','tunnel restoration*','tunnel restorations',1660,1288,0,0,0,NULL,NULL,NULL,NULL),(449,12,'','5814','','','','multiple tunnel restoration*','tunn rests max per tooth',2195,2000,0,0,0,NULL,NULL,NULL,NULL),(450,12,'','5821','58c1','','','1-sfce composite filling*','composite 1 sfce',1610,1288,0,0,0,NULL,NULL,NULL,NULL),(451,12,'','5820','58c1','','','composite filling*','composite max per tooth',2500,2000,0,0,0,NULL,NULL,NULL,NULL),(452,12,'','5822','58c1','','','1 incisal angle','incisal angle',520,416,0,0,0,NULL,NULL,NULL,NULL),(453,12,'','5823','58c1','','','incisal edge','incisal edge',105,84,0,0,0,NULL,NULL,NULL,NULL),(454,12,'','5824','','','','2 incisal angles','2 incisal angles',855,684,0,0,0,NULL,NULL,NULL,NULL),(455,12,'','5825','','','','cusp tip restoration*','buccal cusp tip',1225,980,0,0,0,NULL,NULL,NULL,NULL),(456,12,'','5826','58c2','','1','glass ionomer/silicate filling*','glass ionomer/silicate 1 filling',1465,1172,0,0,0,NULL,NULL,NULL,NULL),(457,12,'','5827','','','MAX','multiple glass ionomer filling*','glass ion max per tooth',2000,1600,0,0,0,NULL,NULL,NULL,NULL),(458,12,'','5831','58d','','','pin/screw retainer*','pin/screw retainer',675,540,0,0,0,NULL,NULL,NULL,NULL),(459,12,'','5836','58e','','1','glass ionomer cement treatment','glass ionomer cement filling',1465,1172,0,0,0,NULL,NULL,NULL,NULL),(460,12,'','5837','','','MAX','multiple glass cement treatment','glass ion cem, max per tooth',2175,1740,0,0,0,NULL,NULL,NULL,NULL),(461,12,'','5838','58','','MAXIMUM','combined fillings (a)','max all restns 1 tooth',3050,2442,0,0,0,NULL,NULL,NULL,NULL),(462,12,'','5839','58','','MAXIMUM','combined fillings (b)','max all restns with p/s or comp adds',3395,2716,0,0,0,NULL,NULL,NULL,NULL),(463,12,'','5841','58d','','','anterior root filling*','root filling 1-3',4620,3696,0,0,0,NULL,NULL,NULL,NULL),(464,12,'','5842','','','','upper premolar root filling*','root filling U 4-5',6290,5032,0,0,0,NULL,NULL,NULL,NULL),(465,12,'','5843','','','','lower premolar root filling*','root filling L 4-5',5450,4360,0,0,0,NULL,NULL,NULL,NULL),(466,12,'','5851','58f1','','','type 1 temporary bridge unit*','temp bridge, >= 3 months (unit)',1730,1384,0,0,0,NULL,NULL,NULL,NULL),(467,12,'','5852','58f2','','','type 2 temporary bridge unit*','temp bridge, < 3 months (unit)',645,516,0,0,0,NULL,NULL,NULL,NULL),(468,12,'','5900','59a','','','full synthetic resin dentures^','sr f/f',17345,13876,0,0,0,NULL,NULL,NULL,NULL),(469,12,'','5901','59a2','','','full synthetic resin upper denture','sr full upper',10820,8656,0,0,0,NULL,NULL,NULL,NULL),(470,12,'','5902','59a2','','','full synthetic resin lower denture','sr full lower',10820,8656,0,0,0,NULL,NULL,NULL,NULL),(471,12,'','5903','59a3','','','partial upper synthetic resin denture','sr partial, 1-3 teeth',6785,5428,0,0,0,NULL,NULL,NULL,NULL),(472,12,'','5903','','','','','ditto, 4-8 teeth',8990,7192,0,0,0,NULL,NULL,NULL,NULL),(473,12,'','5903','','','','','ditto, > 8 teeth',10695,8556,0,0,0,NULL,NULL,NULL,NULL),(474,12,'','5905','59a3','','','partial lower synthetic resin denture','sr partial, 1-3 teeth',6785,5428,0,0,0,NULL,NULL,NULL,NULL),(475,12,'','5905','','','','','ditto, 4-8 teeth',8990,7192,0,0,0,NULL,NULL,NULL,NULL),(476,12,'','5905','','','','','ditto, > 8 teeth',10695,8556,0,0,0,NULL,NULL,NULL,NULL),(477,12,'','5910','','','','','max for any sr comb',21520,17216,0,0,0,NULL,NULL,NULL,NULL),(478,12,'','5904','59a4','','','lingual/palatal bar*','addnl for lingual/palatal bar',1425,1140,0,0,0,NULL,NULL,NULL,NULL),(479,12,'','5911','59b1','','','full metal upper denture','cc/ss full U',15285,12228,0,0,0,NULL,NULL,NULL,NULL),(480,12,'','5912','59b1','','','full metal lower denture','cc/ss full L',15285,12228,0,0,0,NULL,NULL,NULL,NULL),(481,12,'','5916','59b5','','','backing for denture teeth','addnl for backing per tooth',1080,864,0,0,0,NULL,NULL,NULL,NULL),(482,12,'','5916','','','','','max for backing per denture',6450,5160,0,0,0,NULL,NULL,NULL,NULL),(483,12,'','5921','59b6','','discretionary','metal denture*','other metal dentures',0,0,0,0,0,NULL,NULL,NULL,NULL),(484,12,'','5931','59c','','','soft lining (upper)','addnl for soft lining',3570,2856,0,0,0,NULL,NULL,NULL,NULL),(485,12,'','5932','59c','','','soft lining (lower)','addnl for soft lining',3570,2856,0,0,0,NULL,NULL,NULL,NULL),(486,12,'','5941','59d','','','special tray (upper)','special tray',1730,1384,0,0,0,NULL,NULL,NULL,NULL),(487,12,'','5942','59d','','','special tray (lower)','special tray',1730,1384,0,0,0,NULL,NULL,NULL,NULL),(488,12,'','5951','59e','','','metal strip id insert (upper)','metal strip id',550,440,0,0,0,NULL,NULL,NULL,NULL),(489,12,'','5952','59e','','','metal strip id insert (lower)','metal strip id',550,440,0,0,0,NULL,NULL,NULL,NULL),(490,12,'','5952','','','','max fee for resin dentures','max for any sr comb',21520,17216,0,0,0,NULL,NULL,NULL,NULL),(491,12,'','6001','60a','','','deciduous filling','deciduous filling',785,0,0,0,0,NULL,NULL,NULL,NULL),(492,12,'','6002','60b','','','stainless steel crown','stainless steel crown',2065,0,0,0,0,NULL,NULL,NULL,NULL),(493,12,'','6003','60c','','','deciduous pulpotomy','deciduous pulpotomy',825,0,0,0,0,NULL,NULL,NULL,NULL),(494,12,'','6004','60d','','','deciduous pulpectomy','deciduous pulpectomy',1570,0,0,0,0,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `newfeetable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notes`
--

DROP TABLE IF EXISTS `notes`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `notes` (
  `serialno` int(11) NOT NULL,
  `lineno` smallint(5) unsigned NOT NULL,
  `line` varchar(80) default NULL,
  PRIMARY KEY  (`serialno`,`lineno`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

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
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `opid` (
  `id` char(10) NOT NULL,
  `c0` tinyint(3) unsigned default NULL,
  `c1` tinyint(3) unsigned default NULL,
  `c2` tinyint(3) unsigned default NULL,
  `c3` tinyint(3) unsigned default NULL,
  `c4` tinyint(3) unsigned default NULL,
  `c5` tinyint(3) unsigned default NULL,
  `c6` tinyint(3) unsigned default NULL,
  `c7` tinyint(3) unsigned default NULL,
  `c8` tinyint(3) unsigned default NULL,
  `c9` tinyint(3) unsigned default NULL,
  `f0` tinyint(3) unsigned default NULL,
  `f1` tinyint(3) unsigned default NULL,
  `f2` tinyint(3) unsigned default NULL,
  `f3` tinyint(3) unsigned default NULL,
  `f4` tinyint(3) unsigned default NULL,
  `f5` tinyint(3) unsigned default NULL,
  `f6` tinyint(3) unsigned default NULL,
  `f7` tinyint(3) unsigned default NULL,
  `f8` tinyint(3) unsigned default NULL,
  `f9` tinyint(3) unsigned default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `opid`
--

LOCK TABLES `opid` WRITE;
/*!40000 ALTER TABLE `opid` DISABLE KEYS */;
/*!40000 ALTER TABLE `opid` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patients`
--

DROP TABLE IF EXISTS `patients`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `patients` (
  `serialno` int(11) NOT NULL,
  `pf0` tinyint(4) default NULL,
  `pf1` tinyint(4) default NULL,
  `pf2` tinyint(4) default NULL,
  `pf3` tinyint(4) default NULL,
  `pf4` tinyint(4) default NULL,
  `pf5` tinyint(4) default NULL,
  `pf6` tinyint(4) default NULL,
  `pf7` tinyint(4) default NULL,
  `pf8` tinyint(4) default NULL,
  `pf9` tinyint(4) default NULL,
  `pf10` tinyint(4) default NULL,
  `pf11` tinyint(4) default NULL,
  `pf12` tinyint(4) default NULL,
  `pf14` tinyint(4) default NULL,
  `pf15` tinyint(4) default NULL,
  `pf16` tinyint(4) default NULL,
  `pf17` tinyint(4) default NULL,
  `pf18` tinyint(4) default NULL,
  `pf19` tinyint(4) default NULL,
  `money0` int(11) default NULL,
  `money1` int(11) default NULL,
  `money2` int(11) default NULL,
  `money3` int(11) default NULL,
  `money4` int(11) default NULL,
  `money5` int(11) default NULL,
  `money6` int(11) default NULL,
  `money7` int(11) default NULL,
  `money8` int(11) default NULL,
  `money9` int(11) default NULL,
  `money10` int(11) default NULL,
  `pd0` date default NULL,
  `pd1` date default NULL,
  `pd2` date default NULL,
  `pd3` date default NULL,
  `pd4` date default NULL,
  `pd5` date default NULL,
  `pd6` date default NULL,
  `pd7` date default NULL,
  `pd8` date default NULL,
  `pd9` date default NULL,
  `pd10` date default NULL,
  `pd11` date default NULL,
  `pd12` date default NULL,
  `pd13` date default NULL,
  `pd14` date default NULL,
  `sname` varchar(30) default NULL,
  `fname` varchar(30) default NULL,
  `title` varchar(30) default NULL,
  `sex` char(1) default NULL,
  `dob` date default NULL,
  `addr1` varchar(30) default NULL,
  `addr2` varchar(30) default NULL,
  `addr3` varchar(30) default NULL,
  `pcde` varchar(30) default NULL,
  `tel1` varchar(30) default NULL,
  `tel2` varchar(30) default NULL,
  `occup` varchar(30) default NULL,
  `nhsno` varchar(30) default NULL,
  `cnfd` date default NULL,
  `psn` varchar(30) default NULL,
  `cset` varchar(10) default NULL,
  `dnt1` smallint(6) default NULL,
  `dnt2` smallint(6) default NULL,
  `courseno0` int(11) default NULL,
  `courseno1` int(11) default NULL,
  `exempttext` varchar(50) default NULL,
  `ur8st` varchar(34) default NULL,
  `ur7st` varchar(34) default NULL,
  `ur6st` varchar(34) default NULL,
  `ur5st` varchar(34) default NULL,
  `ur4st` varchar(34) default NULL,
  `ur3st` varchar(34) default NULL,
  `ur2st` varchar(34) default NULL,
  `ur1st` varchar(34) default NULL,
  `ul1st` varchar(34) default NULL,
  `ul2st` varchar(34) default NULL,
  `ul3st` varchar(34) default NULL,
  `ul4st` varchar(34) default NULL,
  `ul5st` varchar(34) default NULL,
  `ul6st` varchar(34) default NULL,
  `ul7st` varchar(34) default NULL,
  `ul8st` varchar(34) default NULL,
  `ll8st` varchar(34) default NULL,
  `ll7st` varchar(34) default NULL,
  `ll6st` varchar(34) default NULL,
  `ll5st` varchar(34) default NULL,
  `ll4st` varchar(34) default NULL,
  `ll3st` varchar(34) default NULL,
  `ll2st` varchar(34) default NULL,
  `ll1st` varchar(34) default NULL,
  `lr1st` varchar(34) default NULL,
  `lr2st` varchar(34) default NULL,
  `lr3st` varchar(34) default NULL,
  `lr4st` varchar(34) default NULL,
  `lr5st` varchar(34) default NULL,
  `lr6st` varchar(34) default NULL,
  `lr7st` varchar(34) default NULL,
  `lr8st` varchar(34) default NULL,
  `dent0` tinyint(4) default NULL,
  `dent1` tinyint(4) default NULL,
  `dent2` tinyint(4) default NULL,
  `dent3` tinyint(4) default NULL,
  `exmpt` varchar(10) default NULL,
  `recd` date default NULL,
  `dmask` char(7) default NULL,
  `minstart` smallint(6) default NULL,
  `maxend` smallint(6) default NULL,
  `billdate` date default NULL,
  `billct` tinyint(3) unsigned default NULL,
  `billtype` char(1) default NULL,
  `pf20` tinyint(4) default NULL,
  `money11` int(11) default NULL,
  `pf13` tinyint(4) default NULL,
  `familyno` int(11) default NULL,
  `memo` varchar(255) default NULL,
  `town` varchar(30) default NULL,
  `county` varchar(30) default NULL,
  `mobile` varchar(30) default NULL,
  `fax` varchar(30) default NULL,
  `email1` varchar(50) default NULL,
  `email2` varchar(50) default NULL,
  `status` varchar(30) default NULL,
  `source` varchar(30) default NULL,
  `enrolled` date default NULL,
  `archived` tinyint(4) default '0',
  `initaccept` date default NULL,
  `lastreaccept` date default NULL,
  `lastclaim` date default NULL,
  `expiry` date default NULL,
  `cstatus` tinyint(3) unsigned default NULL,
  `transfer` date default NULL,
  `pstatus` tinyint(3) unsigned default NULL,
  `courseno2` int(11) default NULL,
  PRIMARY KEY  (`serialno`),
  KEY `sname` (`sname`,`fname`),
  KEY `familyno` (`familyno`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `patients`
--

LOCK TABLES `patients` WRITE;
/*!40000 ALTER TABLE `patients` DISABLE KEYS */;
/*!40000 ALTER TABLE `patients` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `perio`
--

DROP TABLE IF EXISTS `perio`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `perio` (
  `serialno` int(11) NOT NULL default '0',
  `chartdate` date NOT NULL default '0000-00-00',
  `bpe` char(6) default NULL,
  `chartdata` blob,
  `flag` tinyint(3) unsigned default NULL,
  PRIMARY KEY  (`serialno`,`chartdate`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `perio`
--

LOCK TABLES `perio` WRITE;
/*!40000 ALTER TABLE `perio` DISABLE KEYS */;
/*!40000 ALTER TABLE `perio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `practitioners`
--

DROP TABLE IF EXISTS `practitioners`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `practitioners` (
  `id` smallint(6) NOT NULL default '0',
  `inits` char(4) default NULL,
  `name` varchar(30) default NULL,
  `apptix` smallint(6) default NULL,
  `formalname` varchar(30) default NULL,
  `fpcno` varchar(20) default NULL,
  `quals` varchar(30) default NULL,
  `datefrom` date default NULL,
  `dateto` date default NULL,
  `flag0` tinyint(4) default NULL,
  `flag1` tinyint(4) default NULL,
  `flag2` tinyint(4) default NULL,
  `flag3` tinyint(4) default NULL,
  `flag4` tinyint(4) default NULL,
  `flag5` tinyint(4) default NULL,
  `flag6` tinyint(4) default NULL,
  `flag7` tinyint(4) default NULL,
  `flag8` tinyint(4) default NULL,
  `flag9` tinyint(4) default NULL,
  `flag10` tinyint(4) default NULL,
  `flag11` tinyint(4) default NULL,
  `flag12` tinyint(4) default NULL,
  `flag13` tinyint(4) default NULL,
  `flag14` tinyint(4) default NULL,
  `flag15` tinyint(4) default NULL,
  `flag16` tinyint(4) default NULL,
  `flag17` tinyint(4) default NULL,
  `flag18` tinyint(4) default NULL,
  `flag19` tinyint(4) default NULL,
  `flag20` tinyint(4) default NULL,
  `flag21` tinyint(4) default NULL,
  `flag22` tinyint(4) default NULL,
  `flag23` tinyint(4) default NULL,
  `flag24` tinyint(4) default NULL,
  `flag25` tinyint(4) default NULL,
  `lastsched` smallint(6) default NULL,
  `currsched` smallint(6) default NULL,
  `schedid` smallint(6) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `practitioners`
--

LOCK TABLES `practitioners` WRITE;
/*!40000 ALTER TABLE `practitioners` DISABLE KEYS */;
/*!40000 ALTER TABLE `practitioners` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sysdata`
--

DROP TABLE IF EXISTS `sysdata`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `sysdata` (
  `currdate` date default NULL,
  `lastdate` date default NULL,
  `siteno` int(11) default NULL,
  `pds` tinyint(4) default NULL,
  `country` tinyint(4) default NULL,
  `audit` tinyint(4) default NULL,
  `notesmode` tinyint(4) default NULL,
  `manualnotesmode` tinyint(4) default NULL,
  `ga` tinyint(4) default NULL,
  `defaultnhs` tinyint(4) default NULL,
  `feestyle` tinyint(4) default NULL,
  `deprivedward` tinyint(4) default NULL,
  `recallbase` tinyint(4) default NULL,
  `recall1` tinyint(4) default NULL,
  `recall2` tinyint(4) default NULL,
  `recall3` tinyint(4) default NULL,
  `receipt` tinyint(4) default NULL,
  `edtactive` tinyint(4) default NULL,
  `apptsactive` tinyint(4) default NULL,
  `apptcheck` tinyint(4) default NULL,
  `ppref0` tinyint(4) default NULL,
  `ppref1` tinyint(4) default NULL,
  `ppref2` tinyint(4) default NULL,
  `ppref3` tinyint(4) default NULL,
  `sstart` tinyint(4) default NULL,
  `tstart` tinyint(4) default NULL,
  `chtsqptr` tinyint(4) default NULL,
  `auditplusp` tinyint(4) default NULL,
  `auditplusrp` tinyint(4) default NULL,
  `fppswd` tinyint(4) default NULL,
  `writecb` tinyint(4) default NULL,
  `sendin` tinyint(4) default NULL,
  `multi` tinyint(4) default NULL,
  `f0` smallint(6) default NULL,
  `f1` smallint(6) default NULL,
  `f2` smallint(6) default NULL,
  `f3` smallint(6) default NULL,
  `f4` smallint(6) default NULL,
  `f5` smallint(6) default NULL,
  `f6` smallint(6) default NULL,
  `f7` smallint(6) default NULL,
  `f8` smallint(6) default NULL,
  `f9` smallint(6) default NULL,
  `addr1` varchar(30) default NULL,
  `addr2` varchar(30) default NULL,
  `addr3` varchar(30) default NULL,
  `telno` varchar(30) default NULL,
  `location` varchar(6) default NULL,
  `pctname` varchar(48) default NULL,
  `col0` int(11) default NULL,
  `col1` int(11) default NULL,
  `col2` int(11) default NULL,
  `col3` int(11) default NULL,
  `col4` int(11) default NULL,
  `col5` int(11) default NULL,
  `col6` int(11) default NULL,
  `col7` int(11) default NULL,
  `col8` int(11) default NULL,
  `col9` int(11) default NULL,
  `col10` int(11) default NULL,
  `col11` int(11) default NULL,
  `col12` int(11) default NULL,
  `col13` int(11) default NULL,
  `col14` int(11) default NULL,
  `col15` int(11) default NULL,
  `col16` int(11) default NULL,
  `col17` int(11) default NULL,
  `col18` int(11) default NULL,
  `col19` int(11) default NULL,
  `a0` smallint(6) default NULL,
  `a1` smallint(6) default NULL,
  `a2` smallint(6) default NULL,
  `a3` smallint(6) default NULL,
  `a4` smallint(6) default NULL,
  `a5` smallint(6) default NULL,
  `a6` smallint(6) default NULL,
  `a7` smallint(6) default NULL,
  `a8` smallint(6) default NULL,
  `a9` smallint(6) default NULL,
  `a10` smallint(6) default NULL,
  `a11` smallint(6) default NULL,
  `a12` smallint(6) default NULL,
  `a13` smallint(6) default NULL,
  `a14` smallint(6) default NULL,
  `a15` smallint(6) default NULL,
  `a16` smallint(6) default NULL,
  `a17` smallint(6) default NULL,
  `a18` smallint(6) default NULL,
  `a19` smallint(6) default NULL,
  `a20` smallint(6) default NULL,
  `a21` smallint(6) default NULL,
  `a22` smallint(6) default NULL,
  `a23` smallint(6) default NULL,
  `a24` smallint(6) default NULL,
  `a25` smallint(6) default NULL,
  `a26` smallint(6) default NULL,
  `a27` smallint(6) default NULL,
  `a28` smallint(6) default NULL,
  `a29` smallint(6) default NULL,
  `bd` blob,
  `serialno` int(11) default NULL,
  `courseno` int(11) default NULL,
  `familyno` int(11) default NULL,
  `coursetype0` varchar(20) default NULL,
  `coursetype1` varchar(20) default NULL,
  `coursetype2` varchar(20) default NULL,
  `coursetype3` varchar(20) default NULL,
  `coursetype4` varchar(20) default NULL,
  `laststart` date default NULL,
  `mainstn` smallint(6) default NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `sysdata`
--

LOCK TABLES `sysdata` WRITE;
/*!40000 ALTER TABLE `sysdata` DISABLE KEYS */;
/*!40000 ALTER TABLE `sysdata` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tsfees`
--

DROP TABLE IF EXISTS `tsfees`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `tsfees` (
  `serialno` int(11) NOT NULL default '0',
  `courseno` int(11) NOT NULL default '0',
  `dent` smallint(6) default NULL,
  `ct` smallint(6) default NULL,
  `data` blob,
  PRIMARY KEY  (`serialno`,`courseno`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `tsfees`
--

LOCK TABLES `tsfees` WRITE;
/*!40000 ALTER TABLE `tsfees` DISABLE KEYS */;
/*!40000 ALTER TABLE `tsfees` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2009-04-27 22:32:07
