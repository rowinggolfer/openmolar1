'''this module has one purpose... provide a connection to the mysqldatabase
using 3rd party MySQLdb module'''

import MySQLdb
from xml.dom import minidom
from openmolar.settings.localsettings import cflocation

currentConnection,myHost,myUser,myPassword,myDb,myPort=None,"","","","",""

class omSQLresult():
    '''
    a class used in returning the result of sql queries
    '''
    def __init__(self):
        self.message=""
        self.number=0
        self.result=False
    def __nonzero__(self):
        '''
        used in case the class is used thus
        if omSQLresult:
        '''
        return self.result


def connect():
    global currentConnection, myHost,myUser,myPassword,myDb,myPort
    if currentConnection==None:
        print "need to parse the settings file"
        dom=minidom.parse(cflocation)
        sysPassword=dom.getElementsByTagName("system_password")[0].firstChild.data
        print sysPassword
        xmlnode=dom.getElementsByTagName("server")[0]
        myHost=xmlnode.getElementsByTagName("location")[0].firstChild.data
        myPort=int(xmlnode.getElementsByTagName("port")[0].firstChild.data)
        xmlnode=dom.getElementsByTagName("database")[0]
        myUser=xmlnode.getElementsByTagName("user")[0].firstChild.data
        myPassword=xmlnode.getElementsByTagName("password")[0].firstChild.data
        myDb=xmlnode.getElementsByTagName("dbname")[0].firstChild.data

    if not (currentConnection and currentConnection.open):
        print "New connection needed"
        print "connecting to %s on %s port %s"%(myDb, myHost, myPort)
        currentConnection=MySQLdb.connect(host=myHost,port=myPort,user=myUser,passwd=myPassword,
                                          db=myDb)
        currentConnection.autocommit(True)
        print currentConnection
    else:
        currentConnection.commit()
    return currentConnection

if __name__=="__main__":
    import time
    print cflocation
    for i in range(1,11):
        try:
            print "connecting....",
            dbc=connect()
            print dbc.info()
            print 'ok... we can make Mysql connections!!'
        except Exception,e:
            print "error",e
        print "loop no ",i
        if i==2:
            #close the db... let's check it reconnects
            dbc.close()
        if i==4:
            #make a slightly bad query... let's check we get a warning
            c=dbc.cursor()
            c.execute('update patients set dob="19691209" where serialno=11956')
            c.close()
        time.sleep(5)

    dbc.close()
