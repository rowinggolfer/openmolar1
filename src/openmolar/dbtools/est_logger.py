# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

'''
this module provides read/write tools for the est_logger database table
'''

import logging

from PyQt4.QtCore import QDate

from openmolar.settings import localsettings
from openmolar.connect import connect

LOGGER = logging.getLogger("openmolar")

SELECT_QUERY = ('select est_data from est_logger '
'where courseno=%s order by ix desc limit 1')

INSERT_QUERY = ('insert into est_logger '
'(courseno, est_data, operator) values (%s,%s,%s)')

HISTORY_QUERY = ('select est_data, operator, time_stamp '
'from est_logger where courseno=%s')

class EstLogger(object):
    def __init__(self, courseno):
        self.courseno = courseno
        self.est_data = ""
        self.get_data()

    def get_data(self):
        db = connect()
        cursor = db.cursor()
        LOGGER.debug(
            'getting last estimate text from est_logger for courseno %s' % (
            self.courseno))

        cursor.execute(SELECT_QUERY, (self.courseno,))

        try:
            self.est_data = cursor.fetchone()[0]
        except TypeError:
            pass

        cursor.close()

    def add_row(self, courseno, est_data):
        '''
        add a row to the daybook table, and save state.
        '''
        if self._write_needed(courseno, est_data):
            db = connect()
            cursor = db.cursor()

            LOGGER.debug('updating est_logger for courseno %s' % courseno)

            values = (courseno, est_data, localsettings.operator)
            cursor.execute(INSERT_QUERY, values)

            cursor.close()
            self.courseno = courseno
            self.est_data = est_data
        else:
            LOGGER.debug("est_logger up to date")

    def _write_needed(self, courseno, est_data):
        return courseno != courseno or est_data != self.est_data

def html_history(courseno):
    db = connect()
    cursor = db.cursor()
    cursor.execute(HISTORY_QUERY, (courseno,))
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        return u'''
        <html>
            <body>
                <h1>%s %s</h1>
            </body>
        </html>'''% (_("No estimate history found for course"), courseno)

    html = u'''<html>
        <body>
            <h1>%s</h1>
            <table width = '100%%' border="1">
    '''% _("Current Estimate Version History")

    html += u'''<tr>
            <th>%s</th>
            <th>%s</th>
            </tr>''' % (
            _("Estimate"),
            _("Author")
            )

    for est_data, author, time_stamp in rows:
        lines = est_data.split("||\n")
        formatted_est = '''<table width="100%%" border="1">
        <tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th>
        <th>%s</th><th>%s</th></tr>'''%(
        _("No."), _("Itemcode"), _("Description"), "CseTyp", _("Feescale"),
        _("Dentist"), _("Fee"), _("Charge"))
        for line in lines:
            formatted_est += "<tr>"
            for i, field in enumerate(line.split(" || ")):
                align = 'align="center"' if i < 6 else 'align="right"'
                formatted_est += "<td %s>%s</td>"% (align, field)
            formatted_est += "</tr>"
        html += u'''<tr>
            <td>%s</table></td>
            <td>%s<br />%s</td>
            </tr>
            ''' % (
            formatted_est, author, time_stamp)

    return html + "</table></body></html>"


if __name__ == "__main__":
    localsettings.initiate()
    LOGGER.setLevel(logging.DEBUG)
    est_logger = EstLogger(1)
    est_logger.add_row(1, "test_data")

    print html_history(1)