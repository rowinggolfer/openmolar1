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

from openmolar.connect import connect
from openmolar.settings import localsettings

QUERY = '''SELECT ix, serialno, author, type, mdate, message FROM ptmemos
WHERE serialno = %s and open = 1 AND
(expiredate is NULL or expiredate >= curdate()) AND (type = %s OR type = "all")
order by ix'''

QUERY_ALL = '''SELECT ix, serialno, author, type, mdate, message,
open, expiredate FROM ptmemos WHERE serialno = %s order by ix'''

INSERT_QUERY = '''INSERT into ptmemos
(serialno, author, type, mdate, expiredate, message, open)
VALUES (%s, %s, %s, NOW(), %s, %s, %s)'''

DELETE_QUERY = "update ptmemos set open = 0 where ix=%s"


class Memo(object):

    def __init__(self):
        self.ix = None
        self.serialno = 0
        self.author = ""
        self.type = ""
        self.mdate = None
        self.expire = None
        self.message = None
        self.open = False

    def setMessage(self, arg):
        self.message = arg


def get_memos(serialno):

    db = connect()

    if localsettings.station == "surgery":
        values = (serialno, "surg")
    elif localsettings.station == "reception":
        values = (serialno, "rec")
    else:
        values = (serialno, "all")

    cursor = db.cursor()
    cursor.execute(QUERY, values)
    rows = cursor.fetchall()
    cursor.close()

    for row in rows:
        memo = Memo()
        memo.ix = row[0]
        memo.serialno = row[1]
        memo.author = row[2]
        memo.type = row[3]
        memo.mdate = row[4]
        memo.setMessage(row[5])
        memo.open = True

        yield memo


def deleteMemo(ix):
    db = connect()
    cursor = db.cursor()
    cursor.execute(DELETE_QUERY, (ix,))
    cursor.close()
    db.commit()


def saveMemo(serialno, author, type, expire, message, open):
    '''
    put a memo into the database
    '''
    db = connect()

    values = (serialno, author, type, expire, message, open)

    cursor = db.cursor()
    result = cursor.execute(INSERT_QUERY, values)
    db.commit()
    cursor.close()

    return result


def html_history(serialno):
    db = connect()
    cursor = db.cursor()
    cursor.execute(QUERY_ALL, (serialno,))
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        return '''
        <html>
            <body>
                <h1>%s</h1>
            </body>
        </html>''' % _("No memo history found")

    html = '''<html>
        <body>
            <h1>%s</h1>
            <table width = '100%%' border="1">
    ''' % _("Memo History")

    html += '''<tr>
            <th>%s</th>
            <th>%s</th>
            <th>%s</th>
            <th>%s</th>
            <th>%s</th>
            <th>%s</th>
            </tr>''' % (
            _("Author"),
            _("Location"),
            _("Date"),
            _("Expires"),
            _("Deleted?"),
            _("Message"))

    for row in rows:
        ix = row[0]
        serialno = row[1]
        author = row[2]
        type = row[3]
        mdate = row[4]
        message = row[5]
        open_ = row[6]
        expiry_date = row[7]
        html += '''<tr>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            </tr>''' % (
            author,
            type,
            localsettings.formatDate(mdate),
            localsettings.formatDate(expiry_date),
            _("Yes") if not open_ else _("No"),
            message)

    return html + "</table></body></html>"


if __name__ == "__main__":
    print(html_history(11956))
