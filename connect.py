'''this module has one purpose... provide a connection to the mysqldatabase
using 3rd party MySQLdb module'''

import MySQLdb

##--local variables----------------------------------------------------------
#
myHost="localhost"              ## put in the ip of your mysql server
myUser="user"                   ## the mysql user
myPassword="password"           ## the mysql password for this user
myDb="openmolar"
##----------------------------------------------------------------------------


def connect():
        return MySQLdb.connect(host=myHost,user=myUser,passwd=myPassword,db=myDb)
if __name__=="__main__":
    try:
        print "opening...",
        db=connect()
        db.close()
        print '''ok... we can make Mysql connections!!
        database - '%s'
        host - '%s'
        using user - '%s'
        and password - '%s' '''%(myDb,myHost,myUser,myPassword)
    except:
        print "error"
