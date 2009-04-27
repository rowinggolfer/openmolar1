# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.


import sys
from openmolar.settings import localsettings
import struct

def toBriefHtml(currEst):
    '''just the final row - ie... current estimate'''
    retarg='<html><body><table width ="100%" border="1"><tr><td colspan="3"><h3>ESTIMATE</h3></td></tr>'
    total=currEst[1]
    for row in currEst[0]:
        retarg+='<tr><td>%s</td><td>%s</td><td align="right">&pound;%d.%02d</td></tr>'%(row[0],row[1],row[2]/100,row[2]%100)
    retarg+='<tr><td></td><td><b>TOTAL<b></td><td align="right"><b>&pound;%d.%02d</b></td></tr>'%(total/100,total%100)
    retarg+='</table></body></htsml>'
    return retarg

def getCurrentEstimate(rows,tsrows):
    dec=()
    if rows!=():
        dec=decode(rows[0][7])
    total=0
    retarg=[]
    for d in dec:
        number_of_items=d[0]
        mult=""
        if int(number_of_items)>1:
            mult="s"
        item=d[1].replace("*",mult)
        if "^" in item:
            item=item.replace("^","")
            number_of_items=""
            
        retarg.append((number_of_items,item,d[2]))  #(d[0],d[1],d[2]))
        total+=d[2]
    dec=()
    if tsrows!=():
        dec=decodeTS(tsrows[0][4])
    for d in dec:
        number_of_items=d[0]
        mult=""
        if int(number_of_items)>1:
            mult="s"
        item=d[1].replace("*",mult)
        if "^" in item:
            item=item.replace("^","")
            number_of_items=""
        retarg.append((number_of_items,item,d[2]))  #(d[0],d[1],d[2]))
        total+=d[2]
    
    return (retarg,total)

def toHtml(estrows,tsrows):  ##########################not really used anymore    18.04.
    retarg="<h3>ESTIMATE</h3>"
    retarg+='<table width="100%" border="1">'
    headers=("Serialno","Course no","Dent","esta","acta","estb","actb")  #,"Decrypted data")
    retarg+='<tr>'
    for header in headers:
        retarg+="<th>%s</th>"%str(header)
    retarg+='<th>Decrypted data</th>'
    retarg+='</tr>'
    total=0
    for estrow in estrows:
        retarg+="<tr>"
        for col in range(7):
            retarg+='<td>%s</td>'%str(estrow[col])
        col=7
        dec=decode(estrow[col])
        retarg+='<td><table border="1">'
        for d in dec:
            retarg+='<tr><td>%s</td><td>%s</td><td align="right">%d</td></tr>'%(d[0],d[1],d[2])
            total+=d[2]
        retarg+='</table></td></tr>\n'

    for estrow in tsrows:
        retarg+='<tr bgcolor="#eeeeee">'
        for col in range(4):
            retarg+='<td>%s</td>'%str(estrow[col])
        retarg+="<td></td>"*3
        col=4
        dec=decodeTS(estrow[col])
        retarg+='<td><table border="1">'
        for d in dec:
            retarg+='<tr><td>%s</td><td>%s</td><td align="right">%d</td></tr>'%(d[0],d[1],d[2])
            total+=d[2]
        retarg+='</table></td></tr>\n'

    retarg+='<tr>'+'<td></td>'*6+'<td><b>TOTAL<b></td><td align="right"><b>%d</b></td></tr>'%total
    retarg+='</table>'
    return retarg

def decode(blob):
    '''estimates are blocks of 8 bytes - format ('N','/x00','ITEM','ITEM','COST','COST','COST','/x00')'''
    retlist=[]
    for i in range(0,len(blob),8):                                              
        number=struct.unpack_from('b',blob,i)[0]                                ## this could be a lot tidier.... struct.unpack(bHi,blob) returns a tuple (number,item,cost)
        item=struct.unpack_from('H',blob,i+2)[0]
        try:
            item_text=localsettings.descriptions['%04d'%item]
        except:
            item_text="unknown item! - '%s'"%item
        cost=struct.unpack_from('i',blob,i+4)[0]
        retlist.append((number,item_text,cost))
    return retlist

def encode(number,item,fee):
    return struct.pack("bHi",number,item,fee)
    

def decodeTS(blob):
    '''estimates are blocks of 8 bytes - format ('N','/x00','ITEM','ITEM','COST','COST','COST','/x00')'''
    retlist=[]
    for i in range(0,len(blob),8): 
        #print struct.unpack("Hbi",blob[i:i+8])
        item=struct.unpack_from('H',blob,i)[0]                                ## this could be a lot tidier.... struct.unpack(bHi,blob) returns a tuple (number,item,cost)
        tooth=struct.unpack_from('B',blob,i+2)[0]
        try:
            item_text=localsettings.descriptions['%04d'%item]
        except:
            item_text="unknown item! - '%s'"%item
        cost=struct.unpack_from('i',blob,i+4)[0]
        print "unknown tooth code",tooth
        retlist.append((1,item_text,cost))
    return retlist
    

if __name__ == "__main__":
    from openmolar.dbtools import patient_class
    localsettings.initiate(False)
    try:
        serialno=int(sys.argv[len(sys.argv)-1])
    except:
        serialno=27223

    pt=patient_class.patient(serialno)
    #print pt.estimates
    #print toHtml(pt.estimates,pt.tsfees)
    
    print toBriefHtml(pt.currEstimate)
    print
    est=((1,101,1950),(2,1739,5600),(1,6521,0))
    blob=encode(est)
    print decode(blob)