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
this module provides read/write tools for the daybook database table
'''

import logging

from PyQt4.QtCore import QDate

from openmolar.settings import localsettings
from openmolar.connect import connect

ALLOW_TX_EDITS = False

LOGGER = logging.getLogger("openmolar")

QUERY = '''insert into daybook
(date, serialno, coursetype, dntid, trtid, diagn, perio, anaes,
misc,ndu,ndl,odu,odl,other,chart,feesa,feesb,feesc)
values (DATE(NOW()),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

HASH_QUERY = 'insert into daybook_link (daybook_id, tx_hash) values (%s, %s)'

INSPECT_QUERY = '''select description, fee, ptfee
from newestimates join est_link2 on newestimates.ix = est_link2.est_id
where tx_hash in
(select tx_hash from daybook join daybook_link on daybook.id = daybook_link.daybook_id where id=%s)'''

DETAILS_QUERY = '''select DATE_FORMAT(date,'%s'), serialno, coursetype, dntid,
        trtid, diagn, perio, anaes, misc, ndu, ndl, odu, odl, other, chart,
        feesa, feesb, feesc, id from daybook
        where {{DENT CONDITIONS}}
        date >= %%s and date <= %%s order by date''' % (
    localsettings.OM_DATE_FORMAT.replace("%", "%%"))

UPDATE_ROW_FEES_QUERY = "update daybook set feesa=%s, feesb=%s where id=%s"
UPDATE_ROW_FEE_QUERY = "update daybook set feesa=%s where id=%s"
UPDATE_ROW_PTFEE_QUERY = "update daybook set feesb=%s where id=%s"
DELETE_ROW_QUERY = "delete from daybook where id=%s"

TREATMENTS_QUERY = ('select diagn, perio, anaes, misc, ndu, ndl, '
                    'odu, odl, other, chart from daybook where id = %s')

UPDATE_TREATMENTS_QUERY = ('update daybook '
                           'set diagn=%s, perio=%s, anaes=%s, misc=%s, ndu=%s, ndl=%s, '
                           'odu=%s, odl=%s, other=%s, chart=%s where id = %s')


def add(sno, cset, dent, trtid, t_dict, fee, ptfee, tx_hashes):
    '''
    add a row to the daybook table
    '''
    db = connect()
    cursor = db.cursor()

    values = (sno, cset, dent, trtid, t_dict["diagn"], t_dict["perio"],
              t_dict["anaes"], t_dict["misc"], t_dict["ndu"], t_dict["ndl"],
              t_dict["odu"], t_dict["odl"], t_dict["other"], t_dict["chart"],
              fee, ptfee, 0)

    LOGGER.debug('updating daybook with the following values: '
                 '%s %s %s %s %s %s %s %s' % (
                     sno, cset, dent, trtid, t_dict, fee, ptfee, 0))

    cursor.execute(QUERY, values)

    daybook_id = db.insert_id()

    for tx_hash in tx_hashes:
        LOGGER.debug("%s %s %s" % (HASH_QUERY, daybook_id, tx_hash))
        cursor.execute(HASH_QUERY, (daybook_id, tx_hash))

    cursor.close()


def details(regdent, trtdent, startdate, enddate):
    '''
    returns an html table, for regdent, trtdent,startdate,enddate
    '''
    dent_conditions = ""
    dents = []
    try:
        if regdent != "*ALL*":
            dent_conditions = 'dntid=%s and '
            dents.append(localsettings.ops_reverse[regdent])
        if trtdent != "*ALL*":
            dent_conditions += 'trtid=%s and '
            dents.append(localsettings.ops_reverse[trtdent])
    except KeyError:
        print "Key Error - %s or %s unregconised" % (regdent, trtdent)
        return '<html><body>%s</body></html>' % _(
            "Error - unrecognised practioner- sorry")

    total, nettotal = 0, 0

    iterDate = QDate(startdate.year(), startdate.month(), 1)

    retarg = '''<html><body>
    <h3>Patients of %s treated by %s between %s and %s (inclusive)</h3>''' % (
        regdent, trtdent,
        localsettings.formatDate(startdate.toPyDate()),
        localsettings.formatDate(enddate.toPyDate()))

    retarg += '''<table width="100%" border="1"><tr><th>DATE</th>
    <th>Dents</th><th>Serial Number</th><th>Name</th>
    <th>Pt Type</th><th>Treatment</th><th></th>
    <th>Gross Fee</th><th>Net Fee</th>'''

    db = connect()
    cursor = db.cursor()

    query = DETAILS_QUERY.replace("{{DENT CONDITIONS}}", dent_conditions)

    while enddate >= iterDate:
        monthtotal, monthnettotal = 0, 0

        if startdate > iterDate:
            queryStartDate = startdate
        else:
            queryStartDate = iterDate

        queryEndDate = iterDate.addMonths(1).addDays(-1)
        if enddate < queryEndDate:
            queryEndDate = enddate

        values = tuple(
            dents + [queryStartDate.toPyDate(), queryEndDate.toPyDate()])

        cursor.execute(query, (values))

        rows = cursor.fetchall()

        for i, row in enumerate(rows):
            retarg += '<tr>' if i % 2 else '<tr bgcolor="#eeeeee">'

            retarg += "<td>%s</td>" % row[0]
            try:
                retarg += '<td> %s / ' % localsettings.ops[row[3]]
            except KeyError:
                retarg += "<td>?? / "
            try:
                retarg += localsettings.ops[row[4]]
            except KeyError:
                retarg += "??"

            retarg += '</td><td>%s</td>' % row[1]

            cursor.execute(
                'select fname,sname from patients where serialno=%s' % row[1])

            names = cursor.fetchall()
            if names != ():
                name = names[0]
                retarg += '<td>%s %s</td>' % (name[0].title(), name[1].title())
            else:
                retarg += "<td>NOT FOUND</td>"
            retarg += '<td>%s</td>' % row[2]

            tx = ""
            for item in (5, 6, 7, 8, 9, 10, 11, 12, 13, 14):
                if row[item] is not None and row[item] != "":
                    tx += "%s " % row[item]

            if ALLOW_TX_EDITS:
                extra_link = ' / <a href="daybook_id_edit?%s">%s</a>' % (
                    row[18], _("Edit Tx"))
            else:
                extra_link = ""

            retarg += '''<td>%s</td>
            <td><a href="daybook_id?%sfeesa=%sfeesb=%s">%s</a>%s</td>
            <td align="right">%s</td>
            <td align="right">%s</td></tr>''' % (tx.strip("%s " % chr(0)),
                                                 row[18], row[15], row[16],
                                                 _("Ests"),
                                                 extra_link,
                                                 localsettings.formatMoney(
                                                 row[15]),
                                                 localsettings.formatMoney(row[16]))

            total += int(row[15])
            monthtotal += int(row[15])

            nettotal += int(row[16])
            monthnettotal += int(row[16])
        retarg += '''<tr><td colspan="6"></td><td><b>%s TOTAL</b></td>
        <td align="right"><b>%s</b></td>
        <td align="right"><b>%s</b></td></tr>''' % (
            localsettings.monthName(iterDate.toPyDate()),
            localsettings.formatMoney(monthtotal),
            localsettings.formatMoney(monthnettotal))
        iterDate = iterDate.addMonths(1)
    cursor.close()
    # db.close()

    retarg += '''<tr><td colspan="6"></td><td><b>GRAND TOTAL</b></td>
    <td align="right"><b>%s</b></td>
    <td align="right"><b>%s</b></td></tr></table></body></html>''' % (
        localsettings.formatMoney(total), localsettings.formatMoney(nettotal))

    return retarg


def inspect_item(id):
    '''
    get more detailed information (by polling the newestimates table
    '''
    db = connect()
    cursor = db.cursor()
    cursor.execute(INSPECT_QUERY, (id, ))
    rows = cursor.fetchall()
    cursor.close()
    return rows


def get_treatments(id):
    '''
    get more detailed information (by polling the newestimates table
    '''
    db = connect()
    cursor = db.cursor()
    cursor.execute(TREATMENTS_QUERY, (id, ))
    row = cursor.fetchone()
    cursor.close()
    return row


def update_treatments(id, treatments):
    values = list(treatments) + [id]
    db = connect()
    cursor = db.cursor()
    result = cursor.execute(UPDATE_TREATMENTS_QUERY, values)
    cursor.close()
    return result


def update_row_fees(id, feesa, feesb):
    db = connect()
    cursor = db.cursor()
    result = cursor.execute(UPDATE_ROW_FEES_QUERY, (feesa, feesb, id))
    cursor.close()
    return result


def update_row_fee(id, feesa):
    db = connect()
    cursor = db.cursor()
    result = cursor.execute(UPDATE_ROW_FEE_QUERY, (feesa, id))
    cursor.close()
    return result


def update_row_ptfee(id, feesb):
    db = connect()
    cursor = db.cursor()
    result = cursor.execute(UPDATE_ROW_PTFEE_QUERY, (feesb, id))
    cursor.close()
    return result


def delete_row(id):
    db = connect()
    cursor = db.cursor()
    result = cursor.execute(DELETE_ROW_QUERY, (id,))
    cursor.close()
    return result


if __name__ == "__main__":
    localsettings.initiate()

    for combo in (("*ALL*", "NW"), ("NW", "AH"), ("NW", "NW")):
        r = details(combo[0], combo[1], QDate(
            2008, 10, 31), QDate(2008, 11, 11))
