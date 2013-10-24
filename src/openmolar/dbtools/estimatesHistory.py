# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.


from openmolar.settings import localsettings
from openmolar.connect import connect
from openmolar.ptModules.estimates import Estimate, TXHash

QUERY = '''SELECT newestimates.ix, number, itemcode, description,
fee, ptfee, feescale, csetype, dent, est_link.completed, tx_hash, courseno
from newestimates right join est_link on newestimates.ix = est_link.est_id
where serialno=%s order by courseno desc, itemcode, ix'''


#QUERY = '''SELECT ix, courseno, number, itemcode, description,
#category, type, fee, ptfee, feescale, csetype, dent, completed
#from newestimates where serialno=%s order by courseno desc, itemcode'''

def getEsts(sno):
    db = connect()
    cursor = db.cursor()
    cursor.execute(QUERY, (sno,))
    rows = cursor.fetchall()
    cursor.close()

    estimates = []

    for row in rows:
        hash_ = row[10]
        completed = bool(row[9])

        tx_hash = TXHash(hash_, completed)

        ix = row[0]

        found = False
        #use existing est if one relates to multiple treatments
        for existing_est in estimates:
            if existing_est.ix == ix:
                existing_est.tx_hashes.append(tx_hash)
                found = True
                break
        if found:
            continue

        #initiate a custom data class
        est = Estimate()

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

        #est.category = "TODO"
        #est.type_ = "TODO"

        est.tx_hashes = [tx_hash]
        estimates.append(est)

        cursor.close()

    return estimates

def details(sno):
    '''
    returns an html page showing pt's old estimates
    '''
    estimatesList = getEsts(sno)
    claimNo = len(estimatesList)
    retarg = "<h2>Past Estimates - %d rows found</h2>"% claimNo
    if claimNo == 0:
        return retarg
    courseno = -1
    firstRow = True
    for est in estimatesList:
        if est.courseno != courseno:
            if not firstRow:
                retarg+="</table>"
                firstRow = False
            retarg += '''</table><h3>Estimate for course number %d</h3>
            <table width="100%%" border="1">'''% est.courseno
            retarg += est.htmlHeader()
            courseno = est.courseno
        retarg += est.toHtmlRow()
    retarg += '</table>\n'

    return retarg

if __name__ == "__main__":
    localsettings.initiate()
    print'<html><body>'
    print details(707).encode("ascii", "replace")
    print "</body></html>"
