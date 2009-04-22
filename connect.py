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
        print "New connection needed"
        currentConnection=MySQLdb.connect(host=myHost,user=myUser,passwd=myPassword,db=myDb)
        currentConnection.autocommit(True)
        print currentConnection
    else:
        currentConnection.commit()
    return currentConnection
    
if __name__=="__main__":
    import time
    for i in range(1,11):
        try:
            print "connecting....",
            db=connect()
            print db.info()
            print 'ok... we can make Mysql connections!!'
        except:
            print "error"
        print "loop no ",i
        if i==2:
            #close the db... let's check it reconnects
            db.close()
        if i==4:
            #make a slightly bad query... let's check we get a warning
            c=db.cursor()
            c.execute('update patients set dob="19691209" where serialno=11956')
            c.close()
        time.sleep(5)
    print dir(db)
    db.close()