# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.


##########################obsolete code I think################################





from openmolar.dbtools import appointments
from openmolar.settings import localsettings
import time

def toHtml(d):
    adate="%d_%02d_%02d"%(d.year(),d.month(),d.day())
    data= appointments.allAppointmentData(adate)
    activeDents=data[0]
    for d in activeDents:
        activeDents[activeDents.index(d)]=localsettings.apptix[d]
    apps=data[1]
    year,month,day=adate.split("_")
    timelist=[int(year),int(month),int(day),8,30,0,0,0,0] #8:30am
    starttime= time.mktime(timelist)
    timelist[3]=19
    timelist[4]=5  #19:05pm  -- needs to be 1 time unit more than finish time
    endtime= time.mktime(timelist)
    curtime=starttime
    times=[]
    headers=[]
    block=0
    while curtime<endtime:
        t=time.localtime(curtime)
        wysdom_timescheme=t[3]*100+t[4]  #which is crap 800,805 etc...
        times.append(wysdom_timescheme)
        if block%3==0:
            headers.append('%d:%02d'%(t[3],t[4])) #which is readable 08:00, 08:05
        block+=1
        curtime+=300 #5 minute slots=5*60

    columnNo=len(times)
    headerString='<tr><td width="80">Practitioner</td>'
    for header in headers:
        headerString+='<td colspan="3" width="70"><a name="%s"></a>%s</td>'%(header,header)
    headerString+="</tr>"
    rowNo=len(activeDents)
    tableDict={}
    for row in activeDents:
        tableDict[row]=[]
        for col in range(columnNo):
            tableDict[row].append("free")
    for app in apps:
        dent=app[1]                                                                                #this will be a number
        astart=app[2]
        afin=app[3]
        name='%s<br />%d<br />%s %s %s<br /><i>%s</i>'%tuple(app[4:10])
        row= dent
        startcol=times.index(astart)
        fincol=times.index(afin)
        for col in range(startcol,fincol):
            apptext=(str(name))
            if tableDict.has_key(row):
                tableDict[row][col]=apptext
            else:
                print "key error ",row
    tBody=""
    for row in activeDents:
        tBody+='<tr><td><b><hr />%s<hr /></b></td>'%row
        i=1
        for col in range(columnNo):
            curcell=tableDict[row][col]
            if col<columnNo-1:
                nextcell=tableDict[row][col+1]
            else: nextcell=""
            if nextcell!=curcell:
                color=("#bbccdd","#bbccee","#bbddff","#aabbcc","#aaccdd","#aaffdd","#bbffee")[random.randint(0,6)]
                if "LUNCH" in curcell: color="green"
                if "//BLOCKED//" in curcell: color="white"
                if "EMERGENCY" in curcell: color="white"
                if "free" in curcell: color="white"; curcell=""
                tBody+='<td colspan=%d bgcolor="%s">%s<br />(%d mins)</td>'%(i,color,curcell,i*5)
                i=1
            else:
                i+=1
        tBody+="</tr>"

    return '<html><body><table border="1">'+headerString+tBody+"</table></body></html>"

if __name__ == "__main__":
    localsettings.initiate(False)
    from PyQt4 import QtCore
    toHtml(QtCore.QDate().currentDate())