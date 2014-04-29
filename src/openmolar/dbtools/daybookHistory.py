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

from __future__ import division
from openmolar.settings import localsettings
from openmolar.connect import connect

QUERY = '''select DATE_FORMAT(date, '%s'), coursetype,
    dntid, trtid, concat(diagn,perio,anaes,misc,ndu,ndl,odu,odl),
    other,chart,feesa,feesb, id from daybook
    where serialno = %%s order by date desc, id desc
    ''' % localsettings.OM_DATE_FORMAT.replace("%", "%%")


def details(sno):
    '''
    returns an html page showing pt's Treatment History
    '''
    db = connect()
    cursor = db.cursor()
    cursor.execute(QUERY, (sno,))
    rows = cursor.fetchall()
    cursor.close()

    claimNo = len(rows)
    retarg = "<h2>Past Treatments - %d rows found</h2>" % claimNo
    if claimNo == 0:
        return retarg
    headers = ("Date", "Csetype", "Dentist", "Clinician",
               "Treatment", "Chart", "", "Fee", "PtCharge")

    retarg += '<table width="100%" border="1"><tr>'
    for header in headers:
        retarg += "<th>%s</th>" % header
    retarg += '</tr>'

    fee_total, ptfee_total = 0, 0
    for i, (
            date_, cset, dnt, trt, tx, tx1, tx2, fee, ptfee, id) in enumerate(rows):

        if tx1 is not None:
            #-- the "other treatment" column allows nulls,
            #-- which stuffs up the sql concat
            tx += tx1
        retarg += '    <tr>' if i % 2 else '    <tr bgcolor="#eeeeee">'

        retarg += '''\n        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td align="center">
        <a href="daybook_id?%sfeesa=%sfeesb=%s">%s</a> /
        <a href="daybook_id_edit?%s">%s</a>
        </td>
        <td align="right">%s</td><td align="right">%s</td>\n</tr>\n''' % (
            date_, cset,
            localsettings.ops.get(dnt),
            localsettings.ops.get(trt),
            tx, tx2.strip("\x00"),
            id, fee, ptfee, _("Ests"),
            id, _("Edit Tx"),
            localsettings.formatMoney(fee),
            localsettings.formatMoney(ptfee)
        )

        fee_total += fee
        ptfee_total += ptfee

    retarg += '''<tr>
    <td colspan="6"></td>
    <td align="right"><b>TOTALS</b></td>
    <td align="right"><b>%s</b></td>
    <td align="right"><b>%s</b></td>\n</tr>\n</table>''' % (
        localsettings.formatMoney(fee_total),
        localsettings.formatMoney(ptfee_total))

    return retarg

if __name__ == "__main__":
    localsettings.initiate()
    print'<html><body>'
    print details(17322).encode("ascii", errors="replace")
    print "</body></html>"
