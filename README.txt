To get openMolar running, you need to do the following.

I will give instructions tested on ubuntu8.10 and 9.04

####INSTALL INSTRUCTIONS#####

----------------------------------------------------------------------------------------------------------------
##CLIENT MACHINE##
ensure depenencies are met on the client machine
~$sudo apt-get install python-mysqldb python-qt4

that's it!

----------------------------------------------------------------------------------------------------------------

##SERVER MACHINE##
ensure dependencies are met on the server machine (which will probably be the same machine as your client for testing purposes, providing a service on "localhost")
~$sudo apt-get install mysql-server

MAKE A CAREFUL NOTE OF THE PASSWORD YOU SET UP FOR THE ROOT MYSQL-USER. YOU CANNOT CREATE A DATABASE WITHOUT THIS.

----------------------------------------------------------------------------------------------------------------


You are ready to try openmolar.

cd into the openmolar directory and type
./openmolar


on first run of openMolar, you set a password for the app, you are given an opportunity to install a test database. 


NB - The test database is currently very limited with only 1 patient. (serial no 1)
But The app will not run without it!


the test database has one operator - "user". So when prompted, enter the system password you just set up, and put "user" into the user1 field.


if you wish to re-initiate your settings at any point, delete the file /etc/openmolar/openmolar.conf, or edit this file (with care)


Any problems, get back to me on rowinggolfer@googlemail.com

regards

Neil Wallace
Updated 8th May 2009
