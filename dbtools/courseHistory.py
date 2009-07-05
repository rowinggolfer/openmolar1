# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.


from openmolar.settings import localsettings
from openmolar.connect import connect
from openmolar.dbtools.patient_class import currtrtmtTableAtts

uppers=('ur8','ur7','ur6','ur5','ur4','ur3','ur2','ur1',
'ul1','ul2','ul3','ul4','ul5','ul6','ul7','ul8')
lowers=('ll8','ll7','ll6','ll5','ll4','ll3','ll2','ll1',
'lr1','lr2','lr3','lr4','lr5','lr6','lr7','lr8')

class txCourse():
    def __init__(self,vals):
        i=0
        for att in currtrtmtTableAtts:
            val=vals[i]
            if val=="":
                val="-"
            self.__dict__[att]=val
            i+=1
    def toHtml(self):
        headers=(("Acceptance Date",self.accd),
        ("Completion Date",self.cmpd),
        ("Exam","%s dated - %s"%(self.examt,self.examd)),)

        retarg='<table width="100%" border="2">'
        retarg+='''<tr><th colspan="3" bgcolor="yellow">
        CourseNo %s</th></tr>'''%self.courseno

        for header in headers:
            retarg+='<tr><th colspan="2">%s</th><td>%s</td></tr>'%header
        #-plan row.
        for planned in ("pl","cmp"):
            if planned=="pl":
                bgcolor=' bgcolor="#eeeeee"'
                retarg+='''<tr>
                <th rowspan="7"%s>PLANNED / INCOMPLETE</th>'''%bgcolor
            else:
                retarg+='<tr><th rowspan="7"%s>COMPLETED</th>'
                bgcolor=""
            for att in ("perio",'xray','anaes','other',"custom"):
                if att!="perio":
                    retarg+="<tr>"
                retarg+="<th%s>%s</th><td%s>%s</td></tr>"%(bgcolor,
                att,bgcolor,self.__dict__[att+planned])
            dentureWork=""
            for att in ('ndu','ndl','odu','odl'):
                val=self.__dict__[att+planned]
                if val!="-":
                    dentureWork+="%s - '%s' "%(att,val)
            if dentureWork=="":
                dentureWork="-"
            retarg+="<tr><th%s>Denture Work</th><td%s>%s</td></tr>"%(
            bgcolor,bgcolor,dentureWork)

            retarg+='''<tr><th%s>Chart</th>
            <td><table width="100%s" border="1"><tr>'''%(bgcolor,"%")
            for att in uppers:
                retarg+='<td align="center"%s>%s</td>'%(bgcolor,att.upper())
            retarg+="</tr><tr>"
            for att in uppers:
                retarg+='<td align="center"%s>%s</td>'%(
                bgcolor,self.__dict__[att+planned])

            retarg+="</tr><tr>"
            for att in uppers:
                retarg+='<td align="center"%s>%s</td>'%(bgcolor,att.upper())
            retarg+="</tr><tr>"
            for att in uppers:
                retarg+='<td align="center"%s>%s</td>'%(
                bgcolor,self.__dict__[att+planned])
            retarg+="</tr></table>"
        retarg+='</tr></table>\n'
        return retarg


def details(sno):
    '''
    returns an html page showing pt's Treatment History
    '''
    db=connect()
    cursor=db.cursor()
    fields=currtrtmtTableAtts
    query=""
    for field in fields:
        if field in ('examd','accd','cmpd'):
            query+='DATE_FORMAT(%s,"%s"),'%(
            field,localsettings.sqlDateFormat)
        else:
            query+=field+","
    query=query.strip(",")
    cursor.execute('''SELECT %s from currtrtmt where serialno=%d
    order by courseno desc'''%(query,sno))

    rows= cursor.fetchall()
    cursor.close()

    courses=[]
    for row in rows:
        course=txCourse(row)
        courses.append(course)

    claimNo=len(courses)
    retarg="<h2>Past Courses of Treatment - %d rows found</h2>"%claimNo
    for course in courses:
        retarg+=course.toHtml()

    retarg+='</table>'

    #db.close()
    return retarg

if __name__ == "__main__":
    localsettings.initiate()
    print'<html><body>'
    print details(17322)
    print "</body></html>"
