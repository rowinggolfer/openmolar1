1# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from openmolar.settings import localsettings

class fees():
    def init(self):
        try:   #this breaks compatibility with the old database schema
            cursor.execute("select USERCODE,code,description,description1,pfa from newfeetable")
            rows=cursor.fetchall()
            for row in rows:
                code=row[0]
                userkey=row[3]
                if code!="":
                    #privateFees[row[0]]=row[2]
                    while privateFees.has_key(code):
                        code+="."
                    privateFees[code]=row[2]
                    descriptions[code]=row[1]
                    if userkey!="" and userkey!=None:
                        feeKey[userkey]=row[0]
                
        except Exception,e:
            print "error loading from newfeetable",e




###########module not used!!!!!!!!!!!
