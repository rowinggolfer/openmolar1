To get openMolar running, you need to do the following.

I will give instructions tested on ubuntu8.10

####INSTALL INSTRUCTIONS#####

##CLIENT MACHINE##
ensure depenencies are met on the client machine
~$sudo apt-get install python-mysqldb python-qt4

that's it!

##SERVER MACHINE##
ensure dependencies are met on the server machine (which will probably be the same machine for testing purposes)
~$sudo apt-get install mysql-server-5.0



##STANDARD MYSQL SERVER SETUP

this assumes you have the server running on your client machine (localhost)
you need to create a database called "openmolar", and set up a non-privileged user.
to do so you need to log into mysql as the root mysql user.
To do this open a terminal and type the following

~$mysql -u root -p

you will be prompted for your mysql root user's password. (this is NOT the same as your sudo password)
all being well, this will get you a mysql prompt, so continue (note the ; used in sql.

mysql>CREATE DATABASE openmolar;

hopefully.. you're still receiving nice messages from mysql... so let's add our user... 
as this is a test database, let's set a user "user" and a password "password". 
(You needn't copy these, but changing will mean you need to tweak the openmolar files also.- see below)

mysql>GRANT ALL ON openmolar.* TO user@localhost IDENTIFIED BY "password";

ok... quit the mysql session by hitting ctrl-C.

let's load in some data - I have supplied a backup file called demoDataBase.sql
to dump this into your newly created database - navigate into the openmolar directory and type

~$mysql -u user -ppassword openmolar < demoDataBase.sql

(note the pp in password... this caught me out 1st time)

AND YOU ARE READY TO GO!!

~$./main.py

leave the password blank, and enter "user" in user1.

you are done!!



###ALTERNATE MYSQL install######
if you have the mysql server running remotely, or refused to use my stupid password... simply 
find the file openmaolar/connect.py, and point it to your newly created test database by altering the variables
myHost
myUser
myPassword
myDb

THANKYOU FOR TRYING OPENMOLAR!!
