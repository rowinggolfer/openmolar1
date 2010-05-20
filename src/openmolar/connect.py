'''this module has one purpose... provide a connection to the mysqldatabase
using 3rd party MySQLdb module'''

import MySQLdb
import sys
import time
import base64
from xml.dom import minidom
from openmolar.settings import localsettings

mainconnection = None

if localsettings.VERBOSE: print "parsing the global settings file"
dom = minidom.parse(localsettings.cflocation)

settingsversion = dom.getElementsByTagName("version")[0].firstChild.data
sysPassword = dom.getElementsByTagName("system_password")[0].firstChild.data

xmlnode = dom.getElementsByTagName("server")[localsettings.chosenserver]
myHost = xmlnode.getElementsByTagName("location")[0].firstChild.data
myPort = int(xmlnode.getElementsByTagName("port")[0].firstChild.data)
sslnode = xmlnode.getElementsByTagName("ssl")

xmlnode = dom.getElementsByTagName("database")[localsettings.chosenserver]
myUser = xmlnode.getElementsByTagName("user")[0].firstChild.data
myPassword = xmlnode.getElementsByTagName("password")[0].firstChild.data
if settingsversion == "1.1":
    myPassword = base64.b64decode(myPassword)

myDb = xmlnode.getElementsByTagName("dbname")[0].firstChild.data

if sslnode and sslnode[0].firstChild.data=="True":
    #-- to enable ssl... add <ssl>True</ssl> to the conf file
    if localsettings.VERBOSE: print "using ssl"
    #-- note, dictionary could have up to 5 params.
    #-- ca, cert, key, capath and cipher
    #-- however, IIUC, just using ca will encrypt the data
    ssl_settings = {'ca': '/etc/mysql/ca-cert.pem'}
else:
    if localsettings.VERBOSE: print "not using ssl (you really should!)"
    ssl_settings = {}

dom.unlink()

GeneralError = MySQLdb.Error
ProgrammingError = MySQLdb.ProgrammingError
IntegrityError = MySQLdb.IntegrityError
OperationalError = MySQLdb.OperationalError

class omSQLresult():
    '''
    a class used in returning the result of sql queries
    '''
    def __init__(self):
        self.message = ""
        self.number = 0
        self.result = False
    
    def __nonzero__(self):
        '''
        used in case the class is used thus
        if omSQLresult:
        '''
        return self.result

    def setMessage(self, arg):
        '''
        set the message associated with the result
        '''
        self.message = arg

    def getMessage(self):
        '''
        get the message associated with the result
        '''
        return self.message

    def setNumber(self, arg):
        '''
        set the number of rows grabbed by the result
        '''
        self.number = arg

    def getNumber(self):
        '''
        get the number of rows grabbed by the result
        '''
        return self.number

def connect():
    '''
    returns a MySQLdb object, connected to the database specified in the
    settings file
    '''
    global mainconnection
    attempts = 0
    while attempts < 150:
        try:
            if not (mainconnection and mainconnection.open):
                print "New connection needed"
                print "connecting to %s on %s port %s"% (myDb, myHost, myPort)
                mainconnection = MySQLdb.connect(host = myHost, port = myPort,
                user = myUser, passwd = myPassword, db = myDb, 
                ssl = ssl_settings)
                mainconnection.autocommit(True)
            else:
                mainconnection.commit()

            return mainconnection
        except MySQLdb.Error, e:
            print e.args[1]
            print "will attempt re-connect in 2 seconds..."
            mainconnection = None
        time.sleep(2)
        
    raise localsettings.omDBerror(e)

if __name__ == "__main__":
    from openmolar.settings import localsettings
    localsettings.initiate()
    import time
    print localsettings.cflocation
    for i in range(1, 11):
        try:
            print "connecting....",
            dbc = connect()
            print dbc.info()
            print 'ok... we can make Mysql connections!!'
            print "loop no ", i
            if i == 2:
                #close the db... let's check it reconnects
                dbc.close()
            if i == 4:
                #make a slightly bad query... let's check we get a warning
                c = dbc.cursor()
                c.execute('update patients set dob="196912091" where serialno=4')
                c.close()
        except Exception,e:
            print "error", Exception, e

        time.sleep(5)

    dbc.close()
