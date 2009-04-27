#! /usr/bin/env python

import MySQLdb

myhost="localhost"
myuser="user" 
database="openmolar"
table="newfeetable"  
columnHeaders=("section","USERCODE","code","oldcode","nhs_note1","max_per_course","description","description1","NF08","NF08_pt","PFA","PFC","PFI","spare1","spare2","spare3","spare4")
columntypes=("smallint(6)","CHAR(20)","CHAR(12)","CHAR(12)","CHAR(20)","CHAR(30)","CHAR(60)","CHAR(60)","INT(11)","INT(11)","INT(11)","INT(11)","INT(11)","CHAR(20)","CHAR(20)","CHAR(20)","CHAR(20)")
#################################




def main(filepath):
    db=MySQLdb.connect(host=myhost,user=myuser,db=database,passwd="focus")   #not using a password for my version
    cursor=db.cursor()
    if True:  #this only needs to be run once - it will throw an error if the columns are already there
        cursor.execute("CREATE TABLE %s (ix SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT, PRIMARY KEY (ix))"%table) 
        db.commit()
        for col in range(len(columnHeaders)):
            cursor.execute("alter table %s add %s %s"%(table,columnHeaders[col],columntypes[col]))
            db.commit()

    f=open(filepath,"r")
    line=f.readline()
    lineno=0
    while line: #read the file line by line
        lineno+=1
        items=line.split("|")
        print "number of items=",len(items)
        if len(items)>len(columnHeaders):
            ### this will happen if there are extra delimiters... data will puke, so instead list it, and enter manually later
            print "skipping inconsistent data in line %d (%s)"%(lineno,line)
        else:
            query=""
            for col in range(len(items)):
                item=columnHeaders[col]#ignore column 1 of the csv
                value=items[col].replace('"','').strip(" ") 
                if col in (0,8,9,10,11,12): #integers
                    intvalue=0
                    try:
                        intvalue=int(value)
                    except:
                        pass
                    query+='%s=%s,'%(item,intvalue)
                else:
                    query+='%s="%s",'%(item,value)
            print "writing line %d to database"%lineno
            fullquery="insert into %s set %s "%(table,query.strip(","))
            print fullquery
            if cursor.execute(fullquery):
                db.commit()
        line=f.readline()
    db.commit()
    cursor.close()
    db.close()


if __name__ == "__main__":
    main(filepath)
    print "script finished"
