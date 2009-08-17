# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from xml.dom import minidom
import time,datetime
from openmolar.settings import localsettings

def getDescriptions():
    try:
        d=minidom.parse(localsettings.referralfile)
        descriptions=d.getElementsByTagName("description")
        desclist=[]
        for description in descriptions:
            desclist.append(description.firstChild.data)
        return desclist
    except :
        return ["error getting settings",localsettings.referralfile]
def getHtml(desc,pt):
    try:
        d=minidom.parse(localsettings.referralfile)
        descriptions=d.getElementsByTagName("description")
        desclist=[]
        found=False
        for description in descriptions:
            if description.firstChild.data==desc:
                found=True
                break
        if found:
            '''this means we have a node with the required address fields etc...'''
            refnode=description.parentNode
            surgeon_postal=refnode.getElementsByTagName("surgeon_postal")[0].firstChild.data
            addressNode=refnode.getElementsByTagName("address")
            lines=addressNode[0].getElementsByTagName("line")
            address=[]
            for line in lines:
                address.append(line.firstChild.data)
            greeting=refnode.getElementsByTagName("surgeon_greeting")[0].firstChild.data
            retarg="<html><body>"
            retarg+="<br />"*6
            retarg+="<b>%s<br />"%surgeon_postal
            for line in address:
                retarg+="%s<br />"%line
            retarg+="</b>"+"<br />"*2
            today=time.localtime()[:3]
            d=datetime.date(today[0],today[1],today[2])
            retarg+="%s, " %("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")[d.weekday()]
            retarg+="%s "%d.day
            retarg+="%s, "%("January","February","March","April","May","June","July","August","September","October","November","December")[d.month-1]
            retarg+= '%s <br /><br />'%d.year
            retarg+="Dear %s,<br />"%greeting
            retarg+='<div align="center"><b>Re. %s %s %s - '%(pt.title.title(),pt.fname.title(),pt.sname.title())
            retarg+='DOB %s</b><br />'%pt.dob
            for val in (pt.addr1,pt.addr2,pt.addr3,pt.town,pt.county):
                if val!="":
                    retarg+=val+","
            if pt.pcde!="":
               retarg+=pt.pcde+"."
            retarg+="<br />Tel - "
            i=0
            for val in (pt.tel1,pt.tel2,pt.mobile):
                if val!="":
                    retarg+=("home ","work ","mobile ")[i]+ val+" "
                i+=1
            retarg+="</div>"
            retarg+="<br />"*(12)
            retarg+="Yours Sincerely,"+"<br />"*4
            retarg+="</body></html>"
            return retarg
        else:
            return ("<html><body>SORRY - we couldn't find letter data for % </body></html>"%desc)

    except Exception,e:
        print e
        return False

if __name__ == "__main__":
    localsettings.initiate()
    from openmolar.dbtools import patient_class
    pt=patient_class.patient(4)
    d= getDescriptions()
    print d
    print getHtml(d[0],pt)