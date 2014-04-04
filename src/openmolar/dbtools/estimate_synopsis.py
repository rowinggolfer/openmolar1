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

from openmolar.settings import localsettings
from openmolar.connect import connect

QUERY = '''SELECT description, ptfee, est_link2.completed
from newestimates right join est_link2 on newestimates.ix = est_link2.est_id
where courseno = %s order by itemcode, description'''


def html(courseno):
    values = (courseno,)
    db = connect()
    cursor = db.cursor()
    cursor.execute(QUERY, values)
    rows = cursor.fetchall()
    cursor.close()

    est_count = len(rows)

    if est_count == 0:
        return "<h2>No Estimate Found</h2>"

    completed, planned = [], []
    for description, fee, comp in rows:
        if comp:
            completed.append(
                (description, fee, localsettings.formatMoney(fee)))
        else:
            planned.append((description, fee, localsettings.formatMoney(fee)))

    n_rows = len(planned)
    if len(completed) > n_rows:
        n_rows = len(completed)

    html_ = '''
    <table>
        <tr>
            <th colspan="2">Planned</th>
            <th> </th>
            <th colspan="2">Completed</th>
        </tr>
    '''
    c_tot, p_tot = 0, 0
    for i in range(n_rows):
        try:
            c_desc, fee, c_fee = completed[i]
            c_tot += fee
        except IndexError:
            c_desc, c_fee = "", ""
        try:
            p_desc, fee, p_fee = planned[i]
            p_tot += fee
        except IndexError:
            p_desc, p_fee = "", ""

        html_ += '''<tr>
        <td width= '30%%'>%s</td>
        <td width= '20%%' align='right'>%s</td>
        <td />
        <td width= '30%%'>%s</td>
        <td width= '20%%' align='right'>%s</td>
        </tr>''' % (
            p_desc, p_fee, c_desc, c_fee)

    html_ += '''<tr>
    <td colspan="2" align='right'><b>%s</b></td>
    <td />
    <td colspan="2" align='right'><b>%s</b></td>
    </tr>''' % (
        localsettings.formatMoney(p_tot), localsettings.formatMoney(c_tot))

    return html_ + "</table><br />"


if __name__ == "__main__":
    print html(41146).encode("ascii", "replace")
