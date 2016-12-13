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
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Dumping data for table `clinical_memos`
--

LOCK TABLES `clinical_memos` WRITE;
/*!40000 ALTER TABLE `clinical_memos` DISABLE KEYS */;
INSERT INTO `clinical_memos` VALUES (1,1,'REC','2014-06-10 20:28:10',0,'This patient is for demonstration purposes only. Any similarity to any person, alive or dead, is entirely unintentional.');
/*!40000 ALTER TABLE `clinical_memos` ENABLE KEYS */;
UNLOCK TABLES;


--
-- Dumping data for table `feescales`
--

LOCK TABLES `feescales` WRITE;
/*!40000 ALTER TABLE `feescales` DISABLE KEYS */;
INSERT INTO `feescales` VALUES (1,1,0,'example feescale','<?xml version=\"1.0\" ?><feescale>\n	<version>0.1</version>\n	<tablename>test_feescale</tablename>\n	<feescale_description>Example Fee Scale</feescale_description>\n	<category>P</category>\n	<header id=\"1\">Diagnosis</header>\n	<header id=\"2\">Preventive Care</header>\n	<header id=\"3\">Periodontal Treatment</header>\n	<header id=\"4\">Conservative Treatment</header>\n	<header id=\"5\">Endodontic Treatment</header>\n	<header id=\"6\">Crowns and Veneers</header>\n	<header id=\"7\">Bridgework</header>\n	<header id=\"8\">Extractions and Surgical Treatment</header>\n	<header id=\"9\">Prostheses</header>\n	<header id=\"10\">Orthodontic Treatment</header>\n	<header id=\"11\">Other Forms of Treatment</header>\n	<start>\n		<year>2013</year>\n		<month>8</month>\n		<day>1</day>\n	</start>\n	<item id=\"E0101\">\n		<section>1</section>\n		<shortcut att=\"exam\">CE</shortcut>\n		<description>clinical examination^</description>\n		<fee>\n			<brief_description>clinical exam</brief_description>\n			<gross>2200</gross>\n			<charge>2200</charge>\n		</fee>\n	</item>\n	<item id=\"E0111\">\n		<section>1</section>\n		<shortcut att=\"exam\">ECE</shortcut>\n		<description>extensive clinical examination^</description>\n		<fee>\n			<brief_description>extensive clinical exam</brief_description>\n			<gross>4500</gross>\n			<charge>4500</charge>\n		</fee>\n	</item>\n	<item id=\"E0121\" obscurity=\"2\">\n		<section>1</section>\n		<shortcut att=\"exam\">FCA</shortcut>\n		<description>full case assessment^</description>\n		<fee>\n			<brief_description>full case assessment^</brief_description>\n			<gross>6000</gross>\n			<charge>6000</charge>\n		</fee>\n	</item>\n	<item id=\"E0201\">\n		<section>1</section>\n		<shortcut att=\"xray\">S</shortcut>\n		<description>small xray*</description>\n		<fee condition=\"item_no=1\">\n			<brief_description>small xrays 1 film</brief_description>\n			<gross>900</gross>\n			<charge>900</charge>\n		</fee>\n		<fee condition=\"item_no=2\">\n			<brief_description>small xrays 2 films</brief_description>\n			<gross>1500</gross>\n			<charge>1500</charge>\n		</fee>\n		<fee condition=\"item_no=3\">\n			<brief_description>small xrays 3 films</brief_description>\n			<gross>2000</gross>\n			<charge>2000</charge>\n		</fee>\n		<fee condition=\"item_no&gt;=4\">\n			<brief_description>small xrays maximum</brief_description>\n			<gross>2500</gross>\n			<charge>2500</charge>\n		</fee>\n	</item>\n	<item id=\"E1401\" obscurity=\"0\">\n		<section>4</section>\n		<shortcut att=\"chart\" type=\"regex\">u[lr][de4-8][MODBP]*$|l[lr][de4-8][MODBL]*$|u[lr][a-c1-3][MIDBP]*$|l[lr][a-c1-3][MIDBL]*$</shortcut>\n		<description>filling*</description>\n		<fee>\n			<brief_description>filling</brief_description>\n			<gross>4500</gross>\n			<charge>4500</charge>\n		</fee>\n	</item>\n	<item id=\"E1001\">\n		<section>3</section>\n		<shortcut att=\"perio\">SP</shortcut>\n		<description>scale and polish^</description>\n		<fee>\n			<brief_description>scale &amp; polish</brief_description>\n			<gross>3300</gross>\n			<charge>3300</charge>\n		</fee>\n		<feescale_forbid>\n			<reason>please add scale and polish to a treatment plan conventionally</reason>\n		</feescale_forbid>\n	</item>\n	<item id=\"E1011\">\n		<section>3</section>\n		<shortcut att=\"perio\">SP+</shortcut>\n		<description>extended scale and polish^</description>\n		<fee>\n			<brief_description>scale &amp; polish &gt; 1 visit</brief_description>\n			<gross>4500</gross>\n			<charge>4500</charge>\n		</fee>\n	</item>\n	<item id=\"E1501\">\n		<section>5</section>\n		<shortcut att=\"chart\" type=\"regex\">[ul][lr][1-3]RT$</shortcut>\n		<description>anterior root filling*</description>\n		<fee>\n			<brief_description>root filling 1-3</brief_description>\n			<gross>19500</gross>\n			<charge>19500</charge>\n		</fee>\n	</item>\n	<item id=\"E1502\">\n		<section>5</section>\n		<shortcut att=\"chart\" type=\"regex\">[ul][lr][45]RT$</shortcut>\n		<description>premolar root filling*</description>\n		<fee>\n			<brief_description>root filling 4-5</brief_description>\n			<gross>19500</gross>\n			<charge>19500</charge>\n		</fee>\n	</item>\n	<item id=\"E1504\">\n		<section>5</section>\n		<shortcut att=\"chart\" type=\"regex\">[ul][lr][6-8]RT$</shortcut>\n		<description>molar root filling*</description>\n		<fee>\n			<brief_description>root filling 6-8</brief_description>\n			<gross>28000</gross>\n			<charge>19500</charge>\n		</fee>\n	</item>\n	<item id=\"E0601\">\n		<section>6</section>\n		<shortcut att=\"chart\" type=\"regex\">[ul][lr][1-8]CR</shortcut>\n		<description>other crown*</description>\n		<fee>\n			<brief_description>unspecified crown</brief_description>\n			<gross>35000</gross>\n			<charge>0</charge>\n		</fee>\n	</item>\n	<item id=\"E0701\">\n		<section>7</section>\n		<shortcut att=\"chart\" type=\"regex\">[ul][lr][1-8]BR</shortcut>\n		<description>bridge unit*</description>\n		<fee>\n			<brief_description>unspecified bridge unit</brief_description>\n			<gross>35000</gross>\n			<charge>0</charge>\n		</fee>\n	</item>\n	<item id=\"E2101\">\n		<section>8</section>\n		<shortcut att=\"chart\" type=\"regex\">u[lr][a-e1-8]EX</shortcut>\n		<description>extraction*</description>\n		<fee condition=\"item_no=1\">\n			<brief_description>extraction, 1 tooth</brief_description>\n			<gross>5500</gross>\n			<charge>5500</charge>\n		</fee>\n		<fee condition=\"item_no=2\">\n			<brief_description>extraction, 2 teeth</brief_description>\n			<gross>6500</gross>\n			<charge>5500</charge>\n		</fee>\n		<fee condition=\"3&lt;=item_no&lt;=4\">\n			<brief_description>extraction, 3-4 teeth</brief_description>\n			<gross>8000</gross>\n			<charge>5500</charge>\n		</fee>\n		<fee condition=\"5&lt;=item_no&lt;=9\">\n			<brief_description>extraction, 5-9 teeth</brief_description>\n			<gross>9000</gross>\n			<charge>5500</charge>\n		</fee>\n		<fee condition=\"10&lt;=item_no&lt;=18\">\n			<brief_description>extraction, 10-18 teeth</brief_description>\n			<gross>12000</gross>\n			<charge>5500</charge>\n		</fee>\n		<fee condition=\"item_no&gt;=18\">\n			<brief_description>extraction, &gt; 18 teeth</brief_description>\n			<gross>15000</gross>\n			<charge>5500</charge>\n		</fee>\n	</item>\n	<complex_shortcut>\n		<shortcut att=\"perio\">SP</shortcut>\n		<addition>\n			<case condition=\"n_txs=1\" handled=\"no\"/>\n			<case condition=\"n_txs=2\">\n				<remove_item id=\"E1001\"/>\n				<add_item id=\"E1011\"/>\n				<message>1 visit scale and polish fee removed from estimate. 2 visit scale and polish fee added instead.</message>\n			</case>\n			<case condition=\"n_txs&gt;2\">\n				<alter_item id=\"E1011\"/>\n				<message>maximum fee already claimed for this treatment. Add Privately, or start a new course.</message>\n			</case>\n		</addition>\n		<removal>\n			<case condition=\"n_txs=1\" handled=\"no\"/>\n			<case condition=\"n_txs=2\">\n				<remove_item id=\"E1011\"/>\n				<add_item id=\"E1001\"/>\n				<message>2 visit scale and polish fee removed from estimate, replaced by 1 visit fee.</message>\n			</case>\n			<case condition=\"n_txs&gt;2\">\n				<alter_item id=\"E1011\"/>\n			</case>\n		</removal>\n	</complex_shortcut>\n	<user_display>\n		<crown_chart_button description=\"Porcelain Jacket\" shortcut=\"CR,PJ\" tooltip=\"any tooth\"/>\n		<crown_chart_button description=\"Gold\" shortcut=\"CR,GO\"/>\n		<crown_chart_button description=\"Porcelain/Precious Metal\" shortcut=\"CR,V1\"/>\n		<crown_chart_button description=\"Temporary\" shortcut=\"CR,T1\"/>\n		<crown_chart_button description=\"Resin\" shortcut=\"CR,SR\"/>\n		<crown_chart_button description=\"Lava\" shortcut=\"CR,LAVA\"/>\n		<crown_chart_button description=\"Opalite\" shortcut=\"CR,OPAL\"/>\n		<crown_chart_button description=\"Emax\" shortcut=\"CR,EMAX\"/>\n		<crown_chart_button description=\"Other\" shortcut=\"CR,OT\"/>\n		<crown_chart_button description=\"RECEMENT\" shortcut=\"CR,RC\"/>\n\n		<post_chart_button description=\"Cast Precious Metal\" shortcut=\"CR,C1\" tooltip=\"Lab Made post\"/>\n		<post_chart_button description=\"Cast Non-Precious Metal\" shortcut=\"CR,C2\" tooltip=\"Lab Made post\"/>\n		<post_chart_button description=\"Pre Fabricated Post\" shortcut=\"CR,C3\" tooltip=\"chairside post\"/>\n		<post_chart_button description=\"Other Post\" shortcut=\"CR,OP\"/>\n\n	</user_display>\n</feescale>');
/*!40000 ALTER TABLE `feescales` ENABLE KEYS */;
UNLOCK TABLES;


LOCK TABLES `formatted_notes` WRITE;
/*!40000 ALTER TABLE `formatted_notes` DISABLE KEYS */;
INSERT INTO `formatted_notes` VALUES (1,1,'2014-06-10','REC',NULL,'opened','System date - 10/06/2014 20:26:37','2014-06-10 19:26:37'),(2,1,'2014-06-10','REC',NULL,'newNOTE','This example patient was added to the demo database today.\n','2014-06-10 19:26:37'),(3,1,'2014-06-10','REC',NULL,'closed','REC 10/06/2014 20:26:37','2014-06-10 19:26:37'),(4,1,'2016-09-14','USER',NULL,'opened','System date - 14/09/2016 13:18:01','2016-09-14 12:18:01'),(5,1,'2016-09-14','USER',NULL,'newNOTE','New note added whilst preparing a demo database for release v1.0\n','2016-09-14 12:18:01'),(6,1,'2016-09-14','USER',NULL,'closed','USER 14/09/2016 13:18:01','2016-09-14 12:18:01');
/*!40000 ALTER TABLE `formatted_notes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `forum`
--

LOCK TABLES `forum` WRITE;
/*!40000 ALTER TABLE `forum` DISABLE KEYS */;
INSERT INTO `forum` VALUES (1,'USER','2016-09-14 13:20:13','An Example Message','A forum is useful for inter surgery communication etc.',1,'EVERYBOD'),(2,'USER','2016-09-14 13:20:56','re. An Example Message','thanks.',1,'EVERYBOD'),(3,'USER','2016-09-14 13:22:05','Another Example message','This message has been marked as important by forum user \"USER\"',1,'USER');
/*!40000 ALTER TABLE `forum` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `forum_important`
--

LOCK TABLES `forum_important` WRITE;
/*!40000 ALTER TABLE `forum_important` DISABLE KEYS */;
INSERT INTO `forum_important` VALUES (3,'USER');
/*!40000 ALTER TABLE `forum_important` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `forum_parents`
--

LOCK TABLES `forum_parents` WRITE;
/*!40000 ALTER TABLE `forum_parents` DISABLE KEYS */;
INSERT INTO `forum_parents` VALUES (1,2);
/*!40000 ALTER TABLE `forum_parents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `forumread`
--

LOCK TABLES `forumread` WRITE;
/*!40000 ALTER TABLE `forumread` DISABLE KEYS */;
INSERT INTO `forumread` VALUES (1,1,'USER','2016-09-14 13:20:13'),(2,1,'USER','2016-09-14 13:20:44'),(3,2,'USER','2016-09-14 13:20:56'),(4,3,'USER','2016-09-14 13:22:05'),(5,3,'USER','2016-09-14 13:22:24');
/*!40000 ALTER TABLE `forumread` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `new_patients`
--

LOCK TABLES `new_patients` WRITE;
/*!40000 ALTER TABLE `new_patients` DISABLE KEYS */;
INSERT INTO `new_patients` VALUES (1,'PATIENT','EXAMPLE','MR','M','1969-12-09','19 UNION STREET','','','INVERNESS','SCOTLAND, UK','IV1 1PP','','','','','','','','',NULL,'P',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'','');
/*!40000 ALTER TABLE `new_patients` ENABLE KEYS */;
UNLOCK TABLES;


--
-- Dumping data for table `patient_dates`
--

LOCK TABLES `patient_dates` WRITE;
/*!40000 ALTER TABLE `patient_dates` DISABLE KEYS */;
INSERT INTO `patient_dates` VALUES (1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `patient_dates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `patient_money`
--

LOCK TABLES `patient_money` WRITE;
/*!40000 ALTER TABLE `patient_money` DISABLE KEYS */;
INSERT INTO `patient_money` VALUES (1,0,0,0,0,0,0,0,0,0,0,0,0);
/*!40000 ALTER TABLE `patient_money` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `standard_letters`
--

LOCK TABLES `standard_letters` WRITE;
/*!40000 ALTER TABLE `standard_letters` DISABLE KEYS */;
INSERT INTO `standard_letters` VALUES (1,'XRay Request Letter','<br />\n<div align=\"center\"><b>XRAY REQUEST</b></div>\n<br />\n<p>You have requested copies of your xrays to take with you to another practice.<br />\nPlease be advise that we are happy to do this, and provide these as Jpeg files on CD-rom.\n</p>\n<p>\nThere is, however, a nominal charge of &pound;15.00 for this service, which is in line with British Dental Association recommendations.\n</p>\n<p>\nShould you wish to proceed, please complete the slip below and return it to us along with your remittance.\nOn receipt of the slip, your xrays will normally be forwarded with 7 working days.\n</p>','\n<br />\n<hr />\n<br />\n<p>\nI hereby request copies of my radiographs be sent to:<br />\n(delete as appropriate)\n<ul>\n<li>\nMy home address (as above)\n</li>\n<li>\nAnother dental practice (please give details overleaf).\n</li>\n</ul>\n</p>\n<p>\nI enclose a cheque for &pound; 15.00\n</p>\n<pre>\nSigned    ________________________________________________\n\nDate      ________________________________________________\n\n{{NAME}}\n(adp number {{SERIALNO}}))\n</pre>\n');
/*!40000 ALTER TABLE `standard_letters` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `static_chart`
--

LOCK TABLES `static_chart` WRITE;
/*!40000 ALTER TABLE `static_chart` DISABLE KEYS */;
INSERT INTO `static_chart` VALUES (1,NULL,16,NULL,NULL,'PV ','CR,LAVA ','MI ','B,GL ','MOD ','MO,CO ','','UE ','IM/TIT IM/ABUT  CR,V1 ','','','GI/MOD RT ','','','','UE ','','','','','OL,CO ','B ','FS ','UE ','','','','','','MOL,CO ','','UE ');
/*!40000 ALTER TABLE `static_chart` ENABLE KEYS */;
UNLOCK TABLES;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-12-12 11:07:07
