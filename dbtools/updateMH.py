# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

import MySQLdb,sys
from openmolar.connect import connect
from openmolar.settings import localsettings

def write(sno,data):
    db=connect()
    cursor = db.cursor()

    result=True
    
    query='insert into mednotes (serialno,drnm,adrtel,curmed,oldmed,allerg,heart,lungs,liver,kidney,bleed,anaes,other)'
    query+=" values %s"%str((sno,)+data)
    
    print query
    try:
        cursor.execute("delete from mednotes where serialno=%d"%sno)
        cursor.execute(query)
    except Exception,e:
        print e
        result=False
    db.commit()
    cursor.close()
    #db.close()

    return result

if __name__ == "__main__":
    newdata=("doctor","address","curmeds","pastmeds","allergies","heart","lungs","liver","bleeding","Kidneys",
    "ops","other")
    write(11956,newdata)
    