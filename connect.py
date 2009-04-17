'''this module has one purpose... provide a connection to the mysqldatabase
using 3rd party MySQLdb module'''

import MySQLdb

##--local variables----------------------------------------------------------
#<start_delete_point>   #this delete point is important for my anonymous code export script.
myHost="localhost" #this computer alternatives - "192.168.88.2" work or "192.168.0.3" home
myUser="user"
myPassword="password"
myDb="openmolar"
#<end_delete_point>
##----------------------------------------------------------------------------

currentConnection=None

def connect():
    global currentConnection
    if not (currentConnection and currentConnection.open):
        print "New connection needed",
        currentConnection=MySQLdb.connect(host=myHost,user=myUser,passwd=myPassword,db=myDb)
        print currentConnection
    return currentConnection
    
if __name__=="__main__":
    import time
    for i in range(1,11):
        try:
            print "connecting",
            db=connect()
            print 'ok... we can make Mysql connections!!'
            
        except:
            print "error"
        print "loop no ",i
        if i==8:db.close()
        time.sleep(5)
    print dir(db)
    db.close()