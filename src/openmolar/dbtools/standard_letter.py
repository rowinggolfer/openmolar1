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

import logging
from collections import namedtuple

from openmolar.connect import connect
from openmolar.settings import localsettings

LOGGER = logging.getLogger("openmolar")

QUERY = \
    "SELECT description, body_text, footer FROM standard_letters ORDER BY description"

INSERT_QUERY = '''INSERT INTO standard_letters
(description, body_text, footer) VALUES (%s, %s, %s)
ON DUPLICATE KEY UPDATE body_text=%s, footer=%s'''

DELETE_QUERY = 'DELETE FROM standard_letters WHERE description=%s'

StandardLetter = namedtuple(
    'StandardLetter',
    ('description',
     'text',
     'footer'))


TEMPLATE = '''
<html>
<body>
<!-- top margin -->
%s
<!-- end of top margin -->
<!-- address -->
<b>
%%s<br />
%%s
</b>
<!-- end of address -->
<br /><br />
<!-- date -->
%%s
<!-- end of date -->
%s
<!-- salutation -->
%%s %%s,
<!-- end of salutation.. -->
<!-- letter body -->
%s
<!-- end of letter body -->
<!-- sign off -->
%%s
<!-- end of sign off -->
%s
<!-- footer -->
<!-- end of footer -->
</body>
</html>
''' % ("<br />" * 6, "<br />" * 4, "<br />" * (12), "<br />" * 6)


def getHtml(pt):
    return TEMPLATE % (pt.name,
                       pt.address.replace("\n", "<br />"),
                       localsettings.longDate(localsettings.currentDay()),
                       _("Dear"),
                       pt.name.title(),
                       _("Yours Sincerely")
                       )


def get_standard_letters():
    db = connect()
    cursor = db.cursor()
    cursor.execute(QUERY)
    for row in cursor.fetchall():
        yield StandardLetter(*row)
    cursor.close()


def insert_letter(letter):
    db = connect()
    cursor = db.cursor()
    result = cursor.execute(
        INSERT_QUERY,
        (letter.description, letter.text,
         letter.footer, letter.text, letter.footer)
    )
    cursor.close()
    if result == 0:
        LOGGER.error("insert_letter failed!")
    elif result == 1:
        LOGGER.info("insert_letter worked!")
    elif result == 2:
        LOGGER.warning("insert_letter updated an existing letter!")
    return result in (1, 2)


def delete_letter(letter):
    db = connect()
    cursor = db.cursor()
    result = cursor.execute(DELETE_QUERY, letter.description)
    cursor.close()
    return result


def insert_letters(letters):
    for letter in letters:
        insert_letter(letter)


def delete_letters(letters):
    for letter in letters:
        delete_letter(letter)

def _test():
    from openmolar.dbtools import patient_class
    pt = patient_class.patient(1)
    return getHtml(pt)

def _test2():
    letter = StandardLetter("test", "test body", "footer")
    insert_letter(letter)
    delete_letter(letter)
    for letter in get_standard_letters():
        LOGGER.debug(letter.description)


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    print _test().encode("ascii", "replace")
    _test2()