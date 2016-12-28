#! /usr/bin/python

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2016 Neil Wallace <neil@openmolar.com>               # #
# #                                                                         # #
# # This file is part of OpenMolar.                                         # #
# #                                                                         # #
# # OpenMolar is free software: you can redistribute it and/or modify       # #
# # it under the terms of the GNU General Public License as published by    # #
# # the Free Software Foundation, either version 3 of the License, or       # #
# # (at your option) any later version.                                     # #
# #                                                                         # #
# # OpenMolar is distributed in the hope that it will be useful,            # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of          # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           # #
# # GNU General Public License for more details.                            # #
# #                                                                         # #
# # You should have received a copy of the GNU General Public License       # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.      # #
# #                                                                         # #
# ########################################################################### #

from collections import OrderedDict

from openmolar.settings import localsettings
from openmolar.connect import connect
from openmolar.ptModules.estimates import Estimate, TXHash

QUERY = '''SELECT newestimates.ix, number, itemcode, description,
fee, ptfee, feescale, csetype, dent, est_link2.completed, tx_hash, courseno
from newestimates right join est_link2 on newestimates.ix = est_link2.est_id
where serialno=%s order by courseno desc, itemcode, ix'''

COURSE_QUERY = QUERY.replace(
    "order by courseno desc,", "and courseno = %s order by")

ALLOW_EDIT = False

EDIT_STRING = '<a href="om://edit_estimate?%%s">%s</a>' % _(
    "Edit this Estimate")


def getEsts(sno, courseno=None):
    db = connect()
    cursor = db.cursor()

    if courseno is None:
        cursor.execute(QUERY, (sno,))
    else:
        cursor.execute(COURSE_QUERY, (sno, courseno))
    rows = cursor.fetchall()
    cursor.close()

    estimates = OrderedDict()

    for row in rows:
        hash_ = row[10]
        completed = bool(row[9])

        tx_hash = TXHash(hash_, completed)

        ix = row[0]

        est = estimates.get(ix, Estimate())
        est.ix = ix
        est.courseno = row[11]
        est.number = row[1]
        est.itemcode = row[2]
        est.description = row[3]
        est.fee = row[4]
        est.ptfee = row[5]
        est.feescale = row[6]
        est.csetype = row[7]
        est.dent = row[8]
        try:
            est.tx_hashes.append(tx_hash)
        except AttributeError:
            est.tx_hashes = [tx_hash]

        estimates[ix] = est

    return list(estimates.values())


def details(sno):
    '''
    returns an html page showing pt's old estimates
    '''
    estimates = getEsts(sno)
    claimNo = len(estimates)
    html = "<h2>%s - %d %s</h2>" % (
        _("Past Estimates"),
        claimNo,
        _("found")
    )
    if claimNo == 0:
        return html
    courseno = None

    for i, est in enumerate(estimates):
        if est.courseno != courseno:
            header = est.htmlHeader()
            if ALLOW_EDIT:
                header = header.replace(
                    "<!--editlink-->",
                    EDIT_STRING % est.courseno
                )

            if i > 0:
                html += "</table><hr />"
            html += '<table width="100%%" border="1">%s' % header
            courseno = est.courseno

        html += est.toHtmlRow()
    html += '</table>\n'

    return html


if __name__ == "__main__":
    localsettings.initiate()
    print('<html><body>%s</body></html>' % details(707))
