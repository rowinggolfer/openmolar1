#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ############################################################################ #
# #                                                                          # #
# # Copyright (c) 2009-2014 Neil Wallace <neil@openmolar.com>                # #
# #                                                                          # #
# # This file is part of OpenMolar.                                          # #
# #                                                                          # #
# # OpenMolar is free software: you can redistribute it and/or modify        # #
# # it under the terms of the GNU General Public License as published by     # #
# # the Free Software Foundation, either version 3 of the License, or        # #
# # (at your option) any later version.                                      # #
# #                                                                          # #
# # OpenMolar is distributed in the hope that it will be useful,             # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of           # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            # #
# # GNU General Public License for more details.                             # #
# #                                                                          # #
# # You should have received a copy of the GNU General Public License        # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.       # #
# #                                                                          # #
# ############################################################################ #

'''
This modules provides functions that read and write to the cashbook
table of the database
'''

from __future__ import division

import logging
import functools

from openmolar.settings import localsettings
from openmolar.connect import connect

LOGGER = logging.getLogger("openmolar")

# this variable allows HISTORIC cashbook entries to be altered (by supervisor)
full_edit = False


def viewitems(obj):
    '''
    provides 2.7 functionality for 2.6 and under
    '''
    for key in obj.keys():
        yield (key, obj[key])


class CashBookCodesDict(dict):

    '''
    A dictionary of cashbookCodes called at module initialisation
    '''

    def __init__(self):
        dict.__init__(self)
        self.get_values()
        try:
            self.viewitems
        except AttributeError:  # patched for python <2.7
            self.viewitems = functools.partial(viewitems, self)

    def get_values(self):
        db = connect()
        cursor = db.cursor()
        try:
            query = "select code,descr from cbcodes where flag>1"
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                self[int(row[0])] = row[1]
            LOGGER.debug("cashbook codes loaded successfully")
        except Exception as exc:
            LOGGER.exception("error loading cashbook codes")
        finally:
            cursor.close()


def paymenttaken(sno, name, dent, csetyp, cash, cheque, card,
                 sundry_cash, sundry_cheque, sundry_card, hdp, other, refund):
    '''
    called when a payment has been taken at the desk
    '''
    if csetyp[:1] == "N":
        codes = (1, 3, 5, 14, 15, 17, 21, 24, 125)
    else:
        codes = (2, 4, 6, 14, 15, 17, 21, 24, 125)
    queries = []
    for i, amount in enumerate(
        (cash, cheque, card, sundry_cash,
         sundry_cheque, sundry_card, hdp, other, refund)
    ):
        if amount != 0:
            queries.append('''
            insert into cashbook set cbdate = date(NOW()),
            ref="%06d", linkid=0, descr="%s", code=%d, dntid=%d, amt=%d
            ''' % (sno, name, codes[i], dent, amount))
    if queries != []:
        db = connect()
        cursor = db.cursor()
        dbOK = True
        for query in queries:
            dbOK = dbOK and cursor.execute(query)
        db.commit()
        cursor.close()
        # db.close()
        return dbOK


def details(dent, startdate, enddate,
            treatment_only=False, sundries_only=False):
    '''
    retrns an html version of the cashbook table
    '''

    db = connect()
    cursor = db.cursor()

    # note - len(headers) is used writing out the html
    headers = ("cbdate", "Serial NO", "Dentist", "Patient", "code", "cash",
               "cheque", "card", "unknown", "amt")

    if full_edit or (startdate.toPyDate() <=
                     localsettings.currentDay() <= enddate.toPyDate()):
        headers += ("edit",)

    if dent == "*ALL*":
        cond1 = ""
        dentist = "All Dentists"
    else:
        dentist = localsettings.ops_reverse[str(dent)]
        cond1 = 'dntid="%s" and ' % dentist

    restriction_header = ""
    if treatment_only:
        cond1 += "(code < 10 or code > 123) and "
        restriction_header = "TREATMENT ONLY"
    elif sundries_only:
        cond1 += "code >=14  and  code <= 18 and "
        restriction_header = "SUNDRIES ONLY"
    else:
        restriction_header = "ALL PAYMENTS"

    #-- note - mysqldb doesn't play nice with DATE_FORMAT
    #-- hence the string is formatted entirely using python formatting
    query = '''select
    DATE_FORMAT(cbdate, '%s'), ref, dntid, descr, code, amt, cbdate, id
    from cashbook where %s cbdate>='%s' and cbdate<='%s'
    order by cbdate''' % (
        localsettings.OM_DATE_FORMAT, cond1,
        startdate.toPyDate(), enddate.toPyDate())

    cursor.execute(query)

    rows = cursor.fetchall()

    retarg = "<h3>Cashbook - "
    retarg += "%s - %s - %s (inclusive) - %s</h3>" % (dentist,
                                                      localsettings.formatDate(
                                                          startdate.toPyDate(
                                                          )),
                                                      localsettings.formatDate(
                                                      enddate.toPyDate()),
                                                      restriction_header)

    retarg += '<table width="100%" border="1"> <tr>'
    for header in headers:
        retarg += "<th>%s</th>" % header
    retarg += '</tr>'
    odd = True
    total, cashTOT, chequeTOT, cardTOT, otherTOT = 0, 0, 0, 0, 0
    for row in rows:
        if odd:
            retarg += '<tr bgcolor="#eeeeee">'
            odd = False
        else:
            retarg += '<tr>'
            odd = True

        #-- a row is  (date,sno,dnt,patient,code,amount)

        retarg += '<td>%s</td><td>%s</td>' % (row[0], row[1])
        retarg += '<td>%s</td>' % localsettings.ops.get(row[2])
        retarg += '<td>%s</td>' % row[3]
        CODE = localsettings.cashbookCodesDict.get(row[4])
        retarg += '<td>%s</td>' % CODE
        amt = row[5]
        amt_str = localsettings.formatMoney(amt)

        if "CASH" in CODE:
            retarg += '<td align="right">%s</td>' % amt_str
            cashTOT += amt
            retarg += "<td> </td>" * 3
        elif "CHEQUE" in CODE:
            retarg += '<td> </td><td align="right">%s</td>' % amt_str
            chequeTOT += amt
            retarg += "<td> </td>" * 2
        elif "CARD" in CODE:
            retarg += "<td> </td>" * 2
            retarg += '<td align="right">%s</td>' % amt_str
            cardTOT += amt
            retarg += "<td> </td>"
        else:
            retarg += "<td> </td>" * 3
            retarg += '<td align="right">%s</td>' % amt_str
            otherTOT += amt

        retarg += '<td align="right">%s</td>' % amt_str
        if len(headers) == 11:
            if full_edit or row[6] == localsettings.currentDay():
                retarg += '''<td align="center">
                <a href="edit_%s">edit</a></td>''' % row[7]
            else:
                retarg += '<td align="center">n/a</a>'
        retarg += '</tr>\n'
        total += amt

    sum_text = "= %s + %s + %s + %s" % (
        localsettings.pence_to_pounds(cashTOT),
        localsettings.pence_to_pounds(chequeTOT),
        localsettings.pence_to_pounds(cardTOT),
        localsettings.pence_to_pounds(otherTOT)
    )

    retarg += '''<tr><td colspan="4">%s</td>
    <td><b>TOTAL</b></td>
    <td align="right"><b>%s</b></td>
    <td align="right"><b>%s</b></td>
    <td align="right"><b>%s</b></td>
    <td align="right"><b>%s</b></td>
    <td align="right"><b>%s</b></td></tr>''' % (
        sum_text.replace("+ -", "- "),
        localsettings.formatMoney(cashTOT),
        localsettings.formatMoney(chequeTOT),
        localsettings.formatMoney(cardTOT),
        localsettings.formatMoney(otherTOT),
        localsettings.formatMoney(total))

    retarg += '</table>'
    cursor.close()
    # db.close()
    return retarg

if __name__ == "__main__":
    from PyQt4.QtCore import QDate

    localsettings.initiate()
    print localsettings.cashbookCodesDict
    print localsettings.cashbookCodesDict.viewitems()
