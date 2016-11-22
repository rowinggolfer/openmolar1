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

'''
this module reads and write to the settings table of the database
'''
import datetime
import logging
import re

from openmolar import connect
from openmolar.settings import localsettings

LOGGER = logging.getLogger("openmolar")

PT_COUNT_QUERY = "select count(*) from new_patients"

DENTIST_DATA_QUERY = '''select id, inits, name, formalname, fpcno, quals
FROM practitioners WHERE flag0=1'''

CLINICIANS_QUERY = '''
SELECT ix, apptix, initials, name, formal_name, qualifications, type,
speciality, data, start_date, end_date FROM
clinicians JOIN clinician_dates on clinicians.ix = clinician_dates.clinician_ix
LEFT JOIN diary_link on ix = diary_link.clinician_ix
'''

ACTIVE_CLINICIANS_QUERY = CLINICIANS_QUERY + \
    '''WHERE start_date<now() AND (end_date IS NULL OR end_date>now());'''

OLD_LOGINS_QUERY = "select id from opid"  # pre schema 3.4
LOGINS_QUERY = "%s where active=True" % OLD_LOGINS_QUERY

INSERT_OPID_QUERY = "INSERT INTO opid (id) values (%s)"

INSERT_CLINICIAN_QUERIES = (
    '''INSERT INTO clinicians
(initials, name, formal_name, qualifications, type, speciality, data, comments)
  VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
''',
    '''
INSERT INTO clinician_dates(clinician_ix, start_date, end_date)
VALUES (%s, %s, %s)
''',
    '''
INSERT INTO diary_link(clinician_ix, apptix)
VALUES (%s, %s)
''')

INSERT_SETTING_QUERY = '''INSERT INTO settings
(value, data, modified_by, time_stamp) values (%s, %s, %s, NOW())'''

UPDATE_SETTING_QUERY = '''UPDATE settings SET
data = %s, modified_by = %s, time_stamp = NOW() where value=%s'''


def insert_login(opid):
    db = connect.connect()
    cursor = db.cursor()
    result = cursor.execute(INSERT_OPID_QUERY, (opid,))
    cursor.close()
    return result


def insertData(value, data, user=None):
    '''
    insert a setting (leaving old values behind)
    '''
    LOGGER.info("saving setting (%s, %s) to settings table", value, data)
    if user is None:
        user = localsettings.operator
    values = (value, data, user)

    db = connect.connect()
    cursor = db.cursor()
    result = cursor.execute(INSERT_SETTING_QUERY, values)
    cursor.close()
    return result


def updateData(value, data, user=None):
    '''
    update a setting - if no update occurs, will insert
    '''
    LOGGER.info("updating setting (%s, %s) to settings table", value, data)
    if user is None:
        user = localsettings.operator
    values = (data, user, value)
    db = connect.connect()
    cursor = db.cursor()
    if cursor.execute(UPDATE_SETTING_QUERY, values):
        cursor.close()
        return True
    return insertData(value, data, user)


def insert_practice_name(practice_name):
    return insertData("practice name", practice_name)


def insert_practice_address(address):
    return insertData("practice address", address)


def insert_clinician(clinician):
    result = False
    comments = "added by client - %s" % datetime.datetime.now().strftime("%c")
    db = connect.connect()
    try:
        db.autocommit = False
        cursor = db.cursor()
        cursor.execute(INSERT_CLINICIAN_QUERIES[0], (clinician.initials,
                                                     clinician.name,
                                                     clinician.formal_name,
                                                     clinician.qualifications,
                                                     clinician.type,
                                                     clinician.speciality,
                                                     clinician.data,
                                                     comments)
                       )

        ix = db.insert_id()
        cursor.execute(INSERT_CLINICIAN_QUERIES[1], (ix,
                                                     clinician.start_date,
                                                     clinician.end_date)
                       )

        if clinician.new_diary:
            cursor.execute(INSERT_CLINICIAN_QUERIES[2], (ix, ix))
        cursor.close()
        db.commit()
        result = True
    except:
        LOGGER.exception("failed to insert clinician")
        db.rollback()
    finally:
        db.autocommit = True
    return result


def insert_bookend(date_):
    '''
    the bookend is the final date used when searching for appointments.
    '''
    assert type(date_) == datetime.date, "insert bookend requires a date"
    return insertData(
        "bookend", "%d,%d,%d" % (date_.year, date_.month, date_.day))


class SettingsFetcher(object):

    def __init__(self):
        self._cursor = None
        self.loaded = False
        self.PT_COUNT = 0

    @property
    def cursor(self):
        if self._cursor is None:
            db = connect.connect()
            self._cursor = db.cursor()
        return self._cursor

    def close_cursor(self):
        if self._cursor is not None:
            self._cursor.close()
            self._cursor = None

    def fetch(self):
        self.cursor.execute(PT_COUNT_QUERY)
        self.PT_COUNT = self.cursor.fetchone()[0]
        self._get_clinicians()
        self.loaded = True
        self.close_cursor()

    def getData(self, key):
        try:
            query = 'select data from settings where value = %s order by ix'
            self.cursor.execute(query, (key,))
            rows = self.cursor.fetchall()
            return rows
        except connect.ProgrammingError:
            return ()

    def get_unique_value(self, key):
        '''
        get a single value from the settings table.
        by default gets the last entry
        '''
        try:
            return self.getData(key)[-1][0]
        except IndexError:
            LOGGER.warning("no key '%s' found in settings", key)

    @property
    def allowed_logins(self):
        try:
            self.cursor.execute(LOGINS_QUERY)
            # will get a column error for schema < 3.4
        except connect.OperationalError:
            return self.existing_logins()
        # grab initials of those currently allowed to log in
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]

    def existing_logins(self):
        self.cursor.execute(OLD_LOGINS_QUERY)
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]

    @property
    def wiki_url(self):
        '''
        the database may know of the url (presumably an internally facing ip)
        for the practice wiki??
        '''
        wiki_url = self.get_unique_value("wikiurl")
        return wiki_url if wiki_url else "http://openmolar.com/wiki"

    @property
    def book_end(self):
        book_end = self.get_unique_value("bookend")
        try:
            year, month, day = book_end.split(",")
            return datetime.date(int(year), int(month), int(day))
        except AttributeError:
            pass
        except ValueError:
            LOGGER.warning("Badly formatted value for bookend in settings")
        return datetime.date.today() + datetime.timedelta(days=183)

    @property
    def practice_name(self):
        name = self.get_unique_value("practice name")
        if name:
            return name
        return _("Example Dental Practice")

    @property
    def practice_address(self):
        address = self.get_unique_value("practice address")
        address_list = [self.practice_name]
        try:
            for line_ in address.split("|"):
                address_list.append(line_)
        except AttributeError:
            address_list += ["My Street", "My Town", "POST CODE"]
        except ValueError:
            LOGGER.warning(
                "Badly formatted value for practice_address in settings")
            address_list.append(str(address))
        return tuple(address_list)

    @property
    def supervisor_pword(self):
        hash_ = self.get_unique_value("supervisor_pword")
        if hash_:
            return hash_
        LOGGER.warning("#" * 30)
        LOGGER.warning("WARNING - no supervisor password is set")
        LOGGER.warning("#" * 30)
        # hash of salted ""
        return "c1219df26de403348e211a314ff2fce58aa6e28d"

    def _get_clinicians(self):
        '''
        poll the database and retrieve all practitioners (past and present)
        '''
        self.ops, self.ops_reverse = {}, {}
        self.apptix_dict, self.apptix_reverse = {}, {}
        active_dent_initials, active_dent_ixs = [], []
        active_hyg_initials, active_hyg_ixs = [], []
        archived_dents, archived_hygs = [], []
        self.dentist_data = {}

        self.cursor.execute(CLINICIANS_QUERY)
        rows = self.cursor.fetchall()
        for (ix, apptix, initials, name, formal_name, qualifications, type_,
             speciality, data, start_date, end_date) in rows:
            self.ops[ix] = initials
            self.ops_reverse[initials] = ix
            today = datetime.date.today()

            if apptix:
                self.apptix_reverse[apptix] = initials
            if start_date <= today and (end_date is None or end_date >= today):
                if apptix:
                    self.apptix_dict[initials] = apptix
                if type_ == 1:
                    active_dent_initials.append(initials)
                    active_dent_ixs.append(ix)
                elif type_ in (2, 3):   # hygienist and therapist
                    active_hyg_initials.append(initials)
                    active_hyg_ixs.append(ix)
            else:
                if type_ == 1:
                    archived_dents.append(ix)
                elif type_ == 2:
                    archived_hygs.append(ix)
            if type_ == 1:
                list_no = ""
                if data:
                    m = re.search("list_no=([^ ]*)", data)
                    if m:
                        list_no = m.groups()[0]

                self.dentist_data[ix] = (
                    initials,
                    name,
                    formal_name,
                    list_no,
                    qualifications)

        self.active_dents = tuple(active_dent_initials), tuple(active_dent_ixs)
        self.active_hygs = tuple(active_hyg_initials), tuple(active_hyg_ixs)
        self.archived_dents = tuple(archived_dents)
        self.archived_hygs = tuple(archived_hygs)

    @property
    def account_footer(self):
        '''
        this is text for the bottom of account letters
        '''
        acc_footer = self.get_unique_value("account footer")
        return acc_footer if acc_footer else _("ACCOUNT FOOTER NOT SET")

    @property
    def debt_collector(self):
        '''
        The name of debt collection services (for strong account letters)
        '''
        debt_col = self.get_unique_value("debt collector")
        return debt_col if debt_col else _("DEBT COLLECTOR NOT SET")

    @property
    def disallowed_forum_posters(self):
        rows = self.getData("disallowed forum poster")
        return [fields[0] for fields in rows]


if __name__ == "__main__":
    sf = SettingsFetcher()
    sf.fetch()

    print(sf.PT_COUNT)
    print(sf.wiki_url)
    print(sf.book_end)
    print(sf.supervisor_pword)
    print(sf.getData("enddate"))
    print(sf.active_dents)
    print(sf.active_hygs)
    print(sf.dentist_data)
    print(sf.account_footer)
    print(sf.debt_collector)
    print(sf.disallowed_forum_posters)
