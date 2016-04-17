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

from collections import namedtuple

from openmolar.settings import localsettings
from openmolar.connect import connect

QUERY = "SELECT description FROM referral_centres"

ADDRESS_QUERY = '''
SELECT greeting, addr1, addr2, addr3, addr4, addr5, addr6, addr7
FROM referral_centres where description = %s'''

EDIT_QUERY = '''SELECT ix, description, greeting, addr1, addr2,
addr3, addr4, addr5, addr6, addr7 FROM referral_centres order by ix'''

UPDATE_QUERY = '''UPDATE referral_centres
SET description=%s, greeting=%s, addr1=%s, addr2=%s,
addr3=%s, addr4=%s, addr5=%s, addr6=%s, addr7=%s WHERE ix=%s'''

INSERT_QUERY = '''INSERT INTO referral_centres
(description, greeting, addr1, addr2, addr3, addr4, addr5, addr6, addr7)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''

DELETE_QUERY = 'DELETE FROM referral_centres WHERE ix=%s'

HTML = '''
<html><body>
<br /><br /><br /><br /><br /><br />
<b>%s</b><!-- referral centre postal address -->
<br /><br />
%s<!-- date -->
<br /><br />
%s<!-- greeting -->
<br />
<div align="center">
<b>%s %s %s - %s %s</b><br /><!-- patient name and dob -->
%s<!-- patient address -->
<br />
%s<!-- patient tel -->
</div>
<br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br />
%s<!-- sign off -->
<br /><br />
</body></html>'''


ReferralCentre = namedtuple(
    'ReferralCentre',
    ('ix', 'description', 'greeting', 'addr1', 'addr2',
     'addr3', 'addr4', 'addr5', 'addr6', 'addr7')
    )


def getDescriptions():
    descriptions = []
    db = connect()
    cursor = db.cursor()
    cursor.execute(QUERY)
    for row in cursor.fetchall():
        descriptions.append(row[0])
    cursor.close()
    return descriptions

def get_referral_centres():
    db = connect()
    cursor = db.cursor()
    cursor.execute(EDIT_QUERY)
    for row in cursor.fetchall():
        yield ReferralCentre(*row)
    cursor.close()

def insert_centres(centres):
    values = []
    for centre in centres:
        values.append((centre.description,
                      centre.greeting,
                      centre.addr1,
                      centre.addr2,
                      centre.addr3,
                      centre.addr4,
                      centre.addr5,
                      centre.addr6,
                      centre.addr7)
                    )
    if values != []:
        db = connect()
        cursor = db.cursor()
        cursor.executemany(INSERT_QUERY, values)
        cursor.close()

def update_centres(centres):
    values = []
    for centre in centres:
        values.append((centre.description,
                      centre.greeting,
                      centre.addr1,
                      centre.addr2,
                      centre.addr3,
                      centre.addr4,
                      centre.addr5,
                      centre.addr6,
                      centre.addr7,
                      centre.ix)
                    )
    if values != []:
        db = connect()
        cursor = db.cursor()
        cursor.executemany(UPDATE_QUERY, values)
        cursor.close()

def delete_centres(centres):
    values = []
    for centre in centres:
        values.append((centre.ix,))
    if values != []:
        db = connect()
        cursor = db.cursor()
        cursor.executemany(DELETE_QUERY, values)
        cursor.close()

def getHtml(description, pt):
    '''
    get the HTML for a letter to
    referral_centre identified by description about this pt
    '''
    db = connect()
    cursor = db.cursor()
    cursor.execute(ADDRESS_QUERY, (description,))
    row = cursor.fetchone()
    cursor.close()
    if not row:
        return HTML

    greeting, addr1, addr2, addr3, addr4, addr5, addr6, addr7 = row

    tel = _("Telephone") + " :- "
    for i, val in enumerate((pt.tel1, pt.tel2, pt.mobile)):
        if val != "":
            tel += "%s %s " % (
                (_("home"), _("work "), _("mobile "))[i],
                val)

    return HTML % (

        "<br />".join(
            [a for a in (
                addr1, addr2, addr3, addr4, addr5, addr6, addr7) if a != ""]),
        localsettings.longDate(localsettings.currentDay()),
        greeting,
        pt.title.title(), pt.fname.title(), pt.sname.title(),
        _("D.O.B."), localsettings.formatDate(pt.dob),
        ",".join(
            [a for a in
             (pt.addr1, pt.addr2, pt.addr3, pt.town,
                  pt.county, pt.pcde) if a != ""]),
        tel,
        _("Yours Sincerely"))


if __name__ == "__main__":
    localsettings.initiate()
    from openmolar.dbtools import patient_class
    pt = patient_class.patient(4)
    d = getDescriptions()
    print(d)
    print(getHtml(d[0], pt))
