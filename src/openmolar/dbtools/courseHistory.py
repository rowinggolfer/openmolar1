# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

'''
a module to search for previous course items
'''

from openmolar.settings import localsettings
from openmolar.connect import connect
from openmolar.dbtools.treatment_course import CURRTRT_ATTS
from openmolar.dbtools import estimatesHistory

uppers = ('ur8', 'ur7', 'ur6', 'ur5', 'ur4', 'ur3', 'ur2', 'ur1',
'ul1', 'ul2', 'ul3', 'ul4', 'ul5', 'ul6', 'ul7', 'ul8')
lowers = ('lr8', 'lr7', 'lr6', 'lr5', 'lr4', 'lr3', 'lr2', 'lr1',
'll1', 'll2', 'll3', 'll4', 'll5', 'll6', 'll7', 'll8')

class txCourse():
    '''
    a custom class to hold the data within a currtrtmt row of the database
    '''
    def __init__(self, vals):
        i = 0
        for att in CURRTRT_ATTS:
            val = vals[i]
            self.__dict__[att] = val
            i += 1

    def toHtml(self):
        '''
        returns an HTML representation of itself
        '''

        retarg = '''<table width = "100%%" border = "2">
        <tr><th colspan = "3" bgcolor = "yellow">CourseNo %s</th>
        <//tr>'''% self.courseno

        headers = [("Acceptance Date", self.accd),
        ("Completion Date", self.cmpd)]

        for header in headers:
            retarg +='<tr><th colspan = "2">%s</th><td>%s</td></tr>\n'% header

        #-plan row.
        for planned in ("pl", "cmp"):
            rows = []

            if planned == "pl":
                bgcolor = ' bgcolor = "#eeeeee"'
                header = "PLANNED / INCOMPLETE"
            else:
                bgcolor = ' bgcolor = "#ddeeee"'
                header = "COMPLETED"
                if self.examt !="":
                    exam_details = self.examt
                    if self.examd and self.examd != self.accd:
                        exam_details += " dated - %s"% self.examd
                    cells = "<th%s>%s</th><td%s>%s</td>"% (bgcolor,
                    _("Exam"), bgcolor, exam_details)
                    rows.append(cells)

            for att, con_att in (
                ("perio",_("perio")),
                ("xray",_('xray')),
                ("anaes",_('anaes')),
                ("other",_('other')),
                ("custom",_("custom"))
                ):
                if self.__dict__[att+planned] != "":
                    cells = "<th%s>%s</th><td%s>%s</td>"% (bgcolor,
                    con_att, bgcolor, self.__dict__[att+planned])
                    rows.append(cells)

            dentureWork = ""
            for att in ('ndu', 'ndl', 'odu', 'odl'):
                val = self.__dict__[att+planned]
                if val != "":
                    dentureWork += "%s - '%s' "% (att, val)
            if dentureWork != "":
                cells = "<th%s>%s</th><td%s>%s</td>"% (
                bgcolor, _("Denture Work"), bgcolor, dentureWork)

                rows.append(cells)

            showChart = False
            cells = '''<th%s>Chart</th><td>
            <table width = "100%%" border = "1"><tr>'''% bgcolor

            for att in uppers:
                work = self.__dict__[att+planned]
                cells += '<td align = "center"%s>%s</td>'% (
                bgcolor, work)
                showChart = showChart or work !=""

            cells += "</tr><tr>"
            for att in uppers:
                cells += '<td align = "center"%s>%s</td>'% (
                bgcolor, att.upper())

            cells += "</tr><tr>"
            for att in lowers:
                cells += '<td align = "center"%s>%s</td>'% (
                bgcolor, att.upper())

            cells += "</tr><tr>"
            for att in lowers:
                work = self.__dict__[att+planned]
                cells += '<td align = "center"%s>%s</td>'% (
                bgcolor, work)
                showChart = showChart or work !=""

            cells += "</tr></table></td>"

            if showChart:
                rows.append(cells)

            row_span = len(rows)

            if rows != []:
                retarg += '<tr><th rowspan = "%s"%s>%s</th>'% (
                row_span, bgcolor,header)
            for row in rows:
                if row == rows[0]:
                    retarg += "%s</tr>\n"% row
                else:
                    retarg += "<tr>%s</tr>\n"% row

        retarg += '</table>\n'
        return retarg


def details(sno):
    '''
    returns an html page showing pt's Treatment History
    '''
    db = connect()
    cursor = db.cursor()
    fields = CURRTRT_ATTS
    query = ""

    for field in fields:
        if field in ('examd', 'accd', 'cmpd'):
            query += 'DATE_FORMAT(%s, "%s"),'% (
            field, localsettings.OM_DATE_FORMAT)

        else:
            query += field+","

    query = query.strip(",")

    cursor.execute('''SELECT %s from currtrtmt2 where serialno = %d
    order by courseno desc'''% (query, sno))

    rows = cursor.fetchall()
    cursor.close()

    courses = []
    for row in rows:
        course = txCourse(row)
        courses.append(course)

    claimNo = len(courses)
    retarg = "<h2>Past Courses of Treatment - %d rows found</h2>"% claimNo

    for course in courses:
        retarg += course.toHtml()
        retarg += "<br /><hr /><br />"
    #db.close()
    return retarg

def all_details(sno):
    '''
    returns an html page showing pt's Treatment History
    '''
    db = connect()
    cursor = db.cursor()
    fields = CURRTRT_ATTS
    query = ""

    for field in fields:
        if field in ('examd', 'accd', 'cmpd'):
            query += 'DATE_FORMAT(%s, "%s"),'% (
            field, localsettings.OM_DATE_FORMAT)

        else:
            query += field + ","

    query = query.strip(",")

    cursor.execute('''SELECT %s from currtrtmt2 where serialno = %d
    order by courseno desc'''% (query, sno))

    rows = cursor.fetchall()
    cursor.close()

    courses = []
    for row in rows:
        course = txCourse(row)
        courses.append(course)

    claimNo = len(courses)
    retarg = "<h2>Past Courses of Treatment - %d rows found</h2>"% claimNo

    estimatesList = estimatesHistory.getEsts(sno)

    for course in courses:
        retarg += course.toHtml()
        estTableStarted = False
        for est in estimatesList:
            if est.courseno == course.courseno:
                if not estTableStarted:
                    retarg+='''<h3>Estimate for course number %d</h3>
                    <table width="100%%" border="1">'''% est.courseno
                    estTableStarted = True
                    retarg += est.htmlHeader()
                retarg += est.toHtmlRow()

        if estTableStarted:
            retarg += '</table>\n'
        else:
            retarg += "no estimate found for courseno %d"% course.courseno
        retarg += "<br /><hr /><br />"
    #db.close()
    return retarg


if __name__ == "__main__":
    localsettings.initiate()
    print'<html><body>'
    print details(17322)
    print "</body></html>"
