# OpenMolar #

OpenMolar is a software application which assists in the running of a UK Based Dental Practice.

## INSTALL INSTRUCTIONS ##

These instructions are based on Ubuntu 8.10 and 9.04. Your mileage may vary!

On the Client Machine, you must ensure that the following dependencies are met:

* python-mysqldb
* python-qt4

`~$ sudo apt-get install python-mysqldb python-qt4`

On the Server Machine, you must ensure that the following dependancy is met:

* mysql-server

`~$ sudo apt-get install mysql-server`

### MAKE A CAREFUL NOTE OF THE PASSWORD YOU SET UP FOR THE ROOT MYSQL-USER. YOU CANNOT CREATE A DATABASE WITHOUT THIS. ###

Now your server and client are set up, you are ready to try openmolar

* cd into the src directory and type

`./main.py`

* On first run of openMolar, you set a password for the app, you are given an opportunity to install a test database. 
** NB - The test database is currently very limited with only 1 patient. (serial no 1), but the app will not run without it!
* The test database has one operator - "user". So when prompted, enter the system password you just set up, and put "user" into the user1 field.
* If you wish to re-initiate your settings at any point, delete the file /etc/openmolar/openmolar.conf, or edit this file (with care)
* When you are ready to perform a full install, type

`python setup.py install`

Any problems, either [raise an issue](https://github.com/rowinggolfer/openmolar1/issues) or [e-mail me](mailto:rowinggolfer@googlemail.com?subject=OpenMolar)
