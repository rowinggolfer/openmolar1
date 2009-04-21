# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. See the GNU General Public License for more details.


import sys
import struct
from openmolar.connect import connect
from openmolar.settings import localsettings

def toHtml((columns,rowHeaders,smallrowHeaders)):
    retarg="<h3>Fees</h3>" 
    retarg+='<table width="100%" border="1">'
    retarg+='<tr><th>ix</th><th>code</th><th>decription</th>'
    values={}
    rows=0
    for column in columns:
        retarg+="<th>%s</th>"%column[0]
        values[rows]=decode(column[2])
        rows+=1
    retarg+='</tr>'
    odd=True
    i=-1
    for row in range(len(values[0])):
        i+=1
        if odd:
            retarg+='<tr bgcolor="#eeeeee">'
            odd=False
        else:
            retarg+='<tr>'
            odd=True
        #retarg+="<td>%d</td>"%i
        retarg+="<td>%s</td><td>%s</td>"%smallrowHeaders[i]
                
        retarg+="<td>%s</td><td>%s</td>"%rowHeaders[i]
        for col in range(len(columns)):
            if col==4:
                retarg+='<td align="right"><b>%s</b></td>'%values[col][row]
            else:
                retarg+='<td align="right">%s</td>'%values[col][row]     
        retarg+="</tr>\n"
    retarg+='</table>'
    return retarg
       
def decode(blob):
    '''decode in blocks of 4 bytes'''
    i=0
    retlist=[]
    for i in range(0,len(blob),4):
        cost=struct.unpack_from('H',blob,i)[0]
        retlist.append(cost)  
    return retlist

def getFees():
    db=connect()
    cursor=db.cursor()
    cursor.execute('select name,label,data from fees')
    feescales = cursor.fetchall()
    cursor.execute('select id,descr from pfkey')
    rowHeaders = cursor.fetchall()
    cursor.execute('select code,abbrv from abbrv')
    smallrowHeaders = cursor.fetchall()
    cursor.close()
    #db.close()
    return (feescales,rowHeaders,smallrowHeaders)

def getPrivateFeeDict():
    db=connect()
    cursor=db.cursor()
    cursor.execute('select data from fees where name = "PFA"')
    feescale = cursor.fetchone()
    cursor.execute('select code from abbrv')
    feescaleKeys = cursor.fetchall()
    retarg={}
    rows=decode(feescale[0])
    i=0
    for key in feescaleKeys:
        if i>=len(rows):
            break
        
        retarg[key[0]]=rows[i]
        i+=1
    return retarg

def feesHtml():
    return toHtml(getFees())

if __name__ == "__main__":
    #localsettings.initiate(False)
    #print localsettings.privateFees
    #print feesHtml()
    print getPrivateFeeDict()