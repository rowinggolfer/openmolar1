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

import ConfigParser
import datetime
import hashlib
import logging
import locale
import os
import re
import subprocess
import sys
import types

from xml.dom import minidom

from openmolar.settings.version import VERSION

LOGGER = logging.getLogger("openmolar")

SUPERVISOR = '05b1f356646c24bf1765f6f1b65aea3bde7247e1'
DBNAME = "default"

# updated 23.05.2014
CLIENT_SCHEMA_VERSION = "2.5"

DB_SCHEMA_VERSION = "unknown"

ENCODING = locale.getpreferredencoding()

FEETABLES = None
WIKIURL = ""
cashbookCodesDict = None

IGNORE_SCHEMA_CHECK = False

locale.setlocale(locale.LC_ALL, '')

try:
    s = _("translation tools are installed successfully")
    LOGGER.debug(s)
except NameError:
    LOGGER.error("installing gettext for translations")
    # - an unelegant hack to get _() on the namespace for testing
    # - main.py will normally do this for us.
    import gettext
    gettext.install("openmolar", unicode=True)


def showVersion():
    '''
    push version details to std out
    '''
    print ("OpenMolar %s" % VERSION)

if LOGGER.level == logging.DEBUG:
    showVersion()

PRACTICE_NAME = "The Academy Dental Practice"

APPOINTMENT_CARD_HEADER = \
    "%s, 19 Union Street\nInverness. tel 01463 232423" % PRACTICE_NAME


APPOINTMENT_CARD_FOOTER = _("Please try and give at least 24 hours notice") +\
    "\n" + _("if you need to change an appointment.")

CORRESPONDENCE_SIG = "The Academy Dental Practice"

MH_HEADER = ("The Academy Dental Practice",
             _("Confidential Medical History Questionaire"))

WINDOWS = False


def determine_path():
    '''
    returns the true working directory, regardless of any symlinks.
    Very useful.
    Borrowed from wxglade.py
    '''
    try:
        root = __file__
        if os.path.islink(root):
            root = os.path.realpath(root)
        retarg = os.path.dirname(os.path.dirname(os.path.abspath(root)))
        return retarg
    except:
        #-- this shouldn't happen!
        print "no __file__ variable found !!!!"
        return os.path.dirname(os.getcwd())

server_names = []
chosenserver = 0


def setChosenServer(i):
    global DBNAME, chosenserver
    chosenserver = i
    try:
        DBNAME = server_names[i]
        LOGGER.debug("DBNAME = %s" % DBNAME)
    except IndexError:
        LOGGER.warning("no server name.. config file is old format?")

wkdir = determine_path()
appt_shortcut_file = os.path.join(wkdir, "resources",
                                  "appointment_shortcuts.xml")
stylesheet = "file://" + os.path.join(wkdir, "resources", "style.css")
printer_png = "file://" + os.path.join(wkdir, "resources", "icons", "ps.png")
money_png = "file://" + os.path.join(wkdir, "resources", "icons", "vcard.png")
LOGOPATH = "file://" + os.path.join(wkdir, "html", "images", "newlogo.png")
resources_location = os.path.join(wkdir, "resources")
resources_path = "file://" + resources_location

if "win" in sys.platform:
    WINDOWS = True
    LOGGER.info("Windows OS detected - modifying settings")
    #-- sorry about this... but cross platform is a goal :(
    global_cflocation = 'C:\\Program Files\\openmolar\\openmolar.conf'
    localFileDirectory = os.path.join(os.environ.get("HOMEPATH"), ".openmolar")
    #-- this next line is necessary because I have to resort to relative
    #-- imports for the css stuff eg... ../resources/style.css
    #-- on linux, the root is always /  on windows... ??
    os.chdir(wkdir)
    resources_path = resources_path.replace(
        "://", ":///").replace(" ", "%20").replace("\\", "/")
    stylesheet = stylesheet.replace(
        "://", ":///").replace(" ", "%20").replace("\\", "/")
    printer_png = printer_png.replace(
        "://", ":///").replace(" ", "%20").replace("\\", "/")
    money_png = money_png.replace(
        "://", ":///").replace(" ", "%20").replace("\\", "/")
    LOGOPATH = LOGOPATH.replace(
        "://", ":///").replace(" ", "%20").replace("\\", "/")

else:
    if not "linux" in sys.platform:
        LOGGER.warning(
            "unknown system platform (mac?) - defaulting to linux settings")
    global_cflocation = '/etc/openmolar/openmolar.conf'
    localFileDirectory = os.path.join(os.environ.get("HOME"), ".openmolar")

cflocation = os.path.join(localFileDirectory, "openmolar.conf")
LOGIN_CONF = os.path.join(localFileDirectory, "autologin.conf")
TEMP_PDF = os.path.join(localFileDirectory, "temp.pdf")
DOCS_DIRECTORY = os.path.join(localFileDirectory, "documents")

if not os.path.exists(DOCS_DIRECTORY):
    os.makedirs(DOCS_DIRECTORY)

# this is updated if correct password is given
successful_login = False

#-- these permissions are for certain admin duties.
permissionsRaised = False
permissionExpire = datetime.datetime.now()


def openPDF(filepath=TEMP_PDF):
    '''
    open a PDF - minimal checks to ensure no malicious files have been
    inserted into my sacred filepaths though.....
    '''
    if not re.match(".*[.]pdf$", filepath):
        raise Exception("%s is not a pdf file" % filepath)
    openFile(filepath)


def openFile(filepath):
    '''
    open a File - minimal checks to ensure no malicious files have been
    inserted into my sacred filepaths though.....
    '''
    if not os.path.exists(filepath):
        raise IOError("%s does not exist" % filepath)

    if "win" in sys.platform:
        os.startfile(filepath)
    else:
        subprocess.Popen(["xdg-open", filepath])

# MESSAGES ####################################################


def about():
    return '''<p>
OpenMolar - open Source dental practice management software.<br />
Version %s<br />
Client Schema Version is %s, DataBase is at version %s<br /><hr />
Copyright (C) 2009-2014 Neil A. Wallace B.Ch.D.<br />
Project Homepage
<a href="http://www.openmolar.com">
http://www.openmolar.com</a>.
</p>
Thanks to <a href="http://rfquerin.org">Richard Querin</a>
for the wonderful icon and Logo.''' % (
        VERSION,
        CLIENT_SCHEMA_VERSION,
        DB_SCHEMA_VERSION)

license = '''<hr />
<p>
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
<br />
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
<br />
You should have received a copy of the GNU General Public License
along with this program.
If not, see <a href = "http://www.gnu.org/licenses">
http://www.gnu.org/licenses</a>.</p>'''


#-- this variable is used when using DATE_FORMAT from the database
#-- this is done by cashbook and daybook etc...
#-- my preference is the UK style dd/mm/YYYY
#-- feel free to change this!!!

OM_DATE_FORMAT = r"%d/%m/%Y"
try:
    OM_DATE_FORMAT = re.sub("y", "Y", locale.nl_langinfo(locale.D_FMT))
except AttributeError:  # will happen on windows
    OM_DATE_FORMAT = r"%d/%m/%Y"

#-- ditto the qt one
QDATE_FORMAT = "dddd, d MMMM yyyy"

#-- updated at login
operator = "unknown"
allowed_logins = []

#-- this list is used for navigating back and forth through the list
recent_snos = []
recent_sno_index = -1
last_family_no = 0

#-- update whenever a manual search is made
#-- sname,fname dob... etc
lastsearch = ("", "", datetime.date(1900, 1, 1), "", "", "")

#-- used to load combobboxes etc....
activedents = []
activehygs = []
activedent_ixs = ()
activehyg_ixs = ()
clinicianNo = 0
clinicianInits = ""

# these times are for the boundaries of the widgets...
earliestStart = datetime.time(8, 0)
latestFinish = datetime.time(20, 0)

#--this dictionary is upated when this file is initiate -
#--it links dentist keys with practioners
#--eg ops[1] = "JJ"
ops = {}

#--keys/dents the other way round.
ops_reverse = {}
apptix = {}
#--this dictionary is upated when this file is initiate -
#--it links appointment keys with practioners
#--eg app[13]="jj"

apptix_reverse = {}

#-- set a latest possible date for appointments to be made
#--(necessary if a very long appointment goes right on through)
#-- would get maximum recursion, quite quickly!
# todo - this will need to change!!!!
bookEnd = datetime.date(2010, 12, 31)

#--treatment codes..

apptTypes = (
    _("EXAM"),
    _("BITE"),
    _("BT"),
    _("FAMILY"),
    _("FILL"),
    _("FIT"),
    _("HYG"),
    _("IMPS"),
    _("LF"),
    _("ORTHO"),
    _("PAIN"),
    _("PREP"),
    _("RCT"),
    _("RECEMENT"),
    _("REVIEW"),
    _("SP"),
    _("TRY"),
    _("XLA")
)

#-- default appt font size
appointmentFontSize = 8

message = ""
dentDict = {}

#-- surgery or reception machine?
station = "surgery"
#-- openmolar needs to know where it is when calling x-rays
surgeryno = -1

#-- pt's are "private, independent, NHS etc...."
CSETYPES = []
DEFAULT_COURSETYPE = ""


#--for debugging purposes... set this to true.- not yet implemented throughout.

#-- self evident
practiceAddress = ("The Academy Dental Practice", "19 Union Street",
                   "Inverness", "IV1 1PP")

#-- this is updated whenever a patient record loads, for ease of address
#-- manipulation
LAST_ADDRESS = ("",) * 8

#-- 1 less dialog box for these lucky people
defaultPrinterforGP17 = False

#-- my own class of excpetion, for when a serialno is called
#--from the database and no match is found


class PatientNotFoundError(Exception):
    pass


def hash_func(message):
    '''
    the function to get a unique value for all treatments in the database
    '''
    return hashlib.sha1(message).hexdigest()


def convert_deciduous(tooth):
    '''
    if the tooth is a match for ulD or llE etc..
    return the corresponding adult tooth
    (necessary to find the attribute used for treatment
    returns tooth unchanged if not a match
    '''
    def my_sub(m):
        return "%s%s" % (m.groups()[0], "*ABCDE".index(m.groups()[1]))
    return re.sub("^([ul][lr])([A-E])", my_sub, tooth)


def currentTime():
    '''
    returns a datetime.datetime.today object
    eg. 7th March 2009 18:56:37 is
    (2009, 3, 7, 18, 56, 37, 582484)
    has attributes day, month, year etc...
    '''
    return datetime.datetime.today()


def int_timestamp():
    '''
    returns the current time in int format
    '''
    d = datetime.datetime.now()

    return int("%d%02d" % (d.hour, d.minute))


def currentDay():
    '''
    return a python date object for the current day
    '''
    return datetime.date.today()


def pence_to_pounds(m):
    '''
    takes an integer, returns as pounds.pence
    eg 1950 -> "19.50"
    '''
    return "%d.%02d" % (m // 100, m % 100)


def formatMoney(m):
    '''
    takes an integer, returns a string
    '''
    if isinstance(m, bytes):
        try:
            retarg = locale.currency(float(m))
            return retarg.decode(ENCODING, "replace")
        except Exception as e:
            print "formatMoney error", e
            return "%s" % m
    else:
        val = pence_to_pounds(m)
        try:
            retarg = locale.currency(float(val))
            return retarg.decode(ENCODING, "replace")
        except Exception as e:
            LOGGER.exception("formatMoney error")
            return val


def previous_sno():
    try:
        return recent_snos[recent_sno_index]
    except IndexError:
        return None


def reverseFormatMoney(m):
    '''
    takes a string (as from above) and returns the value in pence
    >>> reverseFormatMoney("$387.23")
    38723
    '''
    try:
        numbers = re.findall("\d", m)
    except TypeError:
        print "unable to convert %s to an integer - returning 0" % m
        return 0

    retarg = ""
    for number in numbers:
        retarg += number
    return int(retarg)


def GP17formatDate(d):
    '''
    takes a python date type... formats for use on a NHS form
    '''
    try:
        return "%02d%02d%04d" % (d.day, d.month, d.year)
    except AttributeError:
        return " " * 8

try:
    DAYNAMES = (locale.nl_langinfo(locale.DAY_2),
                locale.nl_langinfo(locale.DAY_3),
                locale.nl_langinfo(locale.DAY_4),
                locale.nl_langinfo(locale.DAY_5),
                locale.nl_langinfo(locale.DAY_6),
                locale.nl_langinfo(locale.DAY_7),
                locale.nl_langinfo(locale.DAY_1))
except AttributeError:  # WILL happen on windows - no nl_langinfo
    DAYNAMES = (_("Monday"), _("Tuesday"), _("Wednesday"), _("Thursday"),
                _("Friday"), _("Saturday"), _("Sunday"))


def dayName(d):
    '''
    expects a datetime object, returns the day
    '''
    try:
        return DAYNAMES[d.isoweekday() - 1]
    except IndexError:
        return "?day?"


def monthName(d):
    '''
    expects a datetime object, returns the month
    '''
    try:
        try:
            return("",
                   locale.nl_langinfo(locale.MON_1),
                   locale.nl_langinfo(locale.MON_2),
                   locale.nl_langinfo(locale.MON_3),
                   locale.nl_langinfo(locale.MON_4),
                   locale.nl_langinfo(locale.MON_5),
                   locale.nl_langinfo(locale.MON_6),
                   locale.nl_langinfo(locale.MON_7),
                   locale.nl_langinfo(locale.MON_8),
                   locale.nl_langinfo(locale.MON_9),
                   locale.nl_langinfo(locale.MON_10),
                   locale.nl_langinfo(locale.MON_11),
                   locale.nl_langinfo(locale.MON_12)
                   )[d.month]
        except AttributeError:  # WILL happen on windows - no nl_langinfo
            return("",
                   _("January"),
                   _("February"),
                   _("March"),
                   _("April"),
                   _("May"),
                   _("June"),
                   _("July"),
                   _("August"),
                   _("September"),
                   _("October"),
                   _("November"),
                   _("December"))[d.month]
    except IndexError:
        return "?month?"


def longDate(d):
    try:
        day = str(d.day)
        if day == "1":
            day = day + "st"
        elif day[0] == "1":
            day = day + "th"
        elif day[-1] == "1":
            day = day + "st"
        elif day[-1] == "2":
            day = day + "nd"
        elif day[-1] == "3":
            day = day + "rd"
        else:
            day = day + "th"
        return "%s, %s %s %d" % (dayName(d), day, monthName(d), d.year)
    except Exception as e:
        print e
        return "date"


def readableDate(d):
    '''
    takes a python date type, returns either the date,
    or yesterday, today, tommorrow if necessary
    '''
    if not d:
        return _("None")
    today = currentDay()
    if d == today:
        return _("Today")
    if d - today == datetime.timedelta(1):
        return _("Tomorrow")
    if d - today == datetime.timedelta(-1):
        return _("Yesterday")
    return longDate(d)


def notesDate(d):
    '''
    takes a python date type, returns either the date,
    or yesterday, today, tommorrow if necessary
    '''
    rd = readableDate(d)
    if rd in (_("None"), _("Today"), _("Yesterday")):
        return rd
    try:
        return rd[rd.index(",") + 1:]
    except Exception as exc:
        return "error getting date"


def formatDate(d):
    '''takes a date, returns a formatted date string'''
    try:
        retarg = d.strftime(OM_DATE_FORMAT)
    except AttributeError:
        retarg = ""
    return retarg


def wystimeToHumanTime(t):
    '''converts a time in the format of 0830 or 1420 to "HH:MM" (string)
    >>> wystimeToHumanTime(830)
    '8:30'
    '''
    try:
        hour, min = int(t) // 100, int(t) % 100
        return "%d:%02d" % (hour, min)
    except:
        return None


def wystimeToPyTime(t):
    '''converts a time in the format of 0830 or 1420 to "HH:MM" (string)
    >>> wystimeToPyTime(830)
    datetime.time(8, 30)
    '''
    try:
        hour, min = t // 100, t % 100
        return datetime.time(hour, min)
    except:
        return None


def humanTimetoWystime(t):
    '''reverse function to wystimeToHumanTime
    >>> humanTimetoWystime('8:30')
    830
    '''
    try:
        t = t.replace(":", "")
        return int(t)
    except:
        return None


def minutesPastMidnighttoWystime(t):
    '''
    converts minutes past midnight(int) to format HHMM  (integer)
    >>> minutesPastMidnighttoWystime(100)
    140
    '''
    hour, min = t // 60, int(t) % 60
    return hour * 100 + min


def pyTimetoWystime(t):
    '''
    converts python datetime.time to minutes past midnight(int) to a wystime
    >>> pyTimetoWystime(datetime.time(14,20))
    1420
    '''
    hour, min = t.hour, t.minute
    return hour * 100 + min


def pyTimeToHumantime(t):
    '''
    converts a python datetime.time to format HH:MM
    '''
    return t.strftime("%H:%M")


def minutesPastMidnightToPyTime(t):
    '''
    converts minutes past midnight(int) to a python datetime.time
    >>> minutesPastMidnightToPyTime(100)
    datetime.time(1, 40)
    '''
    hour, min = t // 60, int(t) % 60
    return datetime.time(hour, min)


def pyTimeToMinutesPastMidnight(t):
    '''
    converts python datetime.time to minutes past midnight(int) to a
    >>> pyTimeToMinutesPastMidnight(datetime.time(1, 40))
    100
    '''
    return t.hour * 60 + t.minute


def minutesPastMidnight(t):
    '''
    converts a time in the format of 0830 or 1420
    to minutes past midnight (integer)
    >>> minutesPastMidnight(140)
    100
    '''
    hour, min = int(t) // 100, int(t) % 100
    return hour * 60 + min


def minutesPastMidnighttoPytime(t):
    '''
    converts an integer representing elapsed minutes past midnight to a
    python datetime.time object
    >>> minutesPastMidnighttoPytime(100)
    datetime.time(1, 40)
    '''
    hour, min = t // 60, t % 60
    return datetime.time(hour, min)


def humanTime(t):
    '''
    converts minutes past midnight(int) to format 'HH:MM' (string)
    >>> humanTime(100)
    '1:40'
    '''
    hour, min = t // 60, int(t) % 60
    return "%d:%02d" % (hour, min)


def setOperator(u1, u2):
    global operator
    if u2 == "":
        operator = u1
    else:
        operator = "%s/%s" % (u1, u2)


def autologin():
    '''
    look in ~/.openmolar/login.conf for login options
    '''
    PASSWORD, USER1, USER2 = "", "", ""
    scp = ConfigParser.SafeConfigParser()
    scp.read(LOGIN_CONF)
    try:
        try:
            PASSWORD = scp.get("login", "PASSWORD")
        except ConfigParser.NoOptionError:
            pass
        try:
            USER1 = scp.get("login", "USER1")
        except ConfigParser.NoOptionError:
            pass
        try:
            USER2 = scp.get("login", "USER2")
        except ConfigParser.NoOptionError:
            pass
    except ConfigParser.NoSectionError:
        LOGGER.info("no autologin")

    return PASSWORD, USER1, USER2


def getLocalSettings():
    '''
    check for a local settings file (which has preferences etc...
    and "knows" it's surgery number etc...
    if one doesn't exist... knock one up.
    '''
    global surgeryno, last_forumCheck
    if not os.path.exists(localFileDirectory):
        os.mkdir(localFileDirectory)

    localSets = os.path.join(localFileDirectory, "localsettings.conf")
    if os.path.exists(localSets):
        dom = minidom.parse(localSets)
        node = dom.getElementsByTagName("surgeryno")
        if node and node[0].hasChildNodes():
            surgeryno = int(node[0].firstChild.data)
            LOGGER.debug("setting as surgery number %s" % surgeryno)
        else:
            LOGGER.debug("unknown surgery number")
        dom.unlink()
    else:
        #-- no file found..
        #--so create a settings file.
        f = open(localSets, "w")
        f.write('''<?xml version="1.0" ?>
        <settings><version>1.0</version></settings>
        ''')
        f.close()


def updateLocalSettings(setting, value):
    '''
    adds or updates node "setting" with text value "value"
    '''
    localSets = os.path.join(localFileDirectory, "localsettings.conf")
    LOGGER.debug("updating local settings... %s = %s" % (setting, value))
    dom = minidom.parse(localSets)
    nodes = dom.getElementsByTagName(setting)
    if len(nodes) == 0:
        new_node = dom.createElement(setting)
        dom.firstChild.appendChild(new_node)
        text_node = dom.createTextNode(value)
        new_node.appendChild(text_node)
        dom.firstChild.appendChild(new_node)
    else:
        nodes[0].firstChild.replaceWholeText(value)
    f = open(localSets, "w")
    f.write(dom.toxml())
    f.close()
    dom.unlink()
    return True


def initiateUsers(changedServer=False):
    '''
    just grab user names. necessary because the db schema could be OOD here
    '''
    global allowed_logins
    from openmolar import connect

    if changedServer and connect.mainconnection:
        print "closing connection"
        connect.mainconnection.close()
        reload(connect)

    db = connect.connect()
    cursor = db.cursor()
    cursor.execute("select id from opid")
    # grab initials of those currently allowed to log in
    trows = cursor.fetchall()
    cursor.close()
    allowed_logins = []
    for row in trows:
        allowed_logins.append(row[0])


def initiate(changedServer=False, debug=False):
    # print "initiating settings"
    global message, dentDict, ops, SUPERVISOR, \
        ops_reverse, activedents, activehygs, activedent_ixs, activehyg_ixs, \
        apptix, apptix_reverse, bookEnd, clinicianNo, clinicianInits, \
        WIKIURL, cashbookCodesDict

    from openmolar import connect
    from openmolar.dbtools import db_settings
    from openmolar.dbtools import cashbook

    if changedServer and connect.mainconnection:
        print "closing connection"
        connect.mainconnection.close()
        reload(connect)

    cashbookCodesDict = cashbook.CashBookCodesDict()


    data = db_settings.getData("bookend")
    if data:
        bookEndVals = data[-1][0].split(",")
        bookEnd = datetime.date(int(bookEndVals[0]), int(bookEndVals[1]),
                                int(bookEndVals[2]))

    data = db_settings.getData("supervisor_pword")
    if data:
        SUPERVISOR = data[0][0]
    else:
        LOGGER.warning("#" * 30)
        LOGGER.warning(
            "WARNING - no supervisor password is set, restting to default")
        LOGGER.warning("#" * 30)
        db_settings.updateData("supervisor_pword", SUPERVISOR,
                               "not found reset")

    db = connect.connect()
    cursor = db.cursor()

    # set up four lists with key/value pairs reversedto make for easy
    # referencing

    # first"ops" which is all practitioners
    ops = {}
    ops_reverse = {}
    apptix_reverse = {}
    cursor.execute("select id, inits, apptix from practitioners")
    practitioners = cursor.fetchall()
    for practitioner in practitioners:
        if practitioner[1] is not None:
            ops[practitioner[0]] = practitioner[1]
            ops_reverse[practitioner[1]] = practitioner[0]
            if practitioner[2] != 0:
                apptix_reverse[practitioner[2]] = practitioner[1]
        else:
            ops[0] = "NONE"
            ops_reverse["NONE"] = 0

    try:
        # correspondence details for NHS forms
        query = ("select id,inits,name,formalname,fpcno,quals "
                 "from practitioners where flag0=1")

        cursor.execute(query)
        practitioners = cursor.fetchall()
        dentDict = {}
        for practitioner in practitioners:
            dentDict[practitioner[0]] = practitioner[1:]

        # now get only practitioners who have an active daybook
        query = "select apptix,inits from practitioners where flag3=1"
        cursor.execute(query)
        practitioners = cursor.fetchall()
        apptix = {}
        for practitioner in practitioners:
            if practitioner[0] != 0 and practitioner[0] is not None:  # apptix
                apptix[practitioner[1]] = practitioner[0]

        cursor.execute(
            "select apptix, inits from practitioners where flag3=1 and flag0=1")
        # dentists where appts active
        ixs, activedents = [], []
        practitioners = cursor.fetchall()
        for ix, inits in practitioners:
            ixs.append(ix)
            activedents.append(inits)
        activedent_ixs = tuple(ixs)

        cursor.execute(
            "select apptix, inits from practitioners where flag3=1 and flag0=0")
        # hygenists where appts active
        practitioners = cursor.fetchall()
        ixs, activehygs = [], []
        for ix, inits in practitioners:
            ixs.append(ix)
            activehygs.append(inits)
        activehyg_ixs = tuple(ixs)

    except Exception as exc:
        LOGGER.exception("error loading practitioners")

    #-- set the clinician if possible
    u1 = operator.split("/")[0].strip(" ")
    if u1 in activedents + activehygs:
        clinicianNo = ops_reverse.get(u1)
        clinicianInits = u1
    else:
        LOGGER.debug("no clinician set!")

    getLocalSettings()

    WIKIURL = db_settings.getWikiUrl()

    message = '''<html><head>
    <link rel="stylesheet" href="%s" type="text/css">
    </head><body><div align="center">
    <img src="%s" width="150", height="100", align="left" />
    <img src="%s" width="150", height="100", align="right" />
    <h1>%s</h1>
    <ul><li class="about">%s %s</li></ul><br clear="all" />
    <p>%s</p><p>%s</p></div></body></html>
    ''' % (stylesheet,
            LOGOPATH,
            LOGOPATH,
            _("Welcome to OpenMolar!"),
            _("Version"),
            VERSION,
            _("Your Data is Accessible, and the server reports no issues."),
            _("Have a great day!")
            )

    if debug:
        print "LOCALSETTINGS CALLED WITH DEBUG = TRUE"
        print "ops = ", ops
        print "ops_reverse = ", ops_reverse
        print "apptix = ", apptix
        print "apptix_reverse = ", apptix_reverse
        print "activedents =", activedents
        print "activehygs =", activehygs
        print "allowed logins =", allowed_logins
        print "stylesheet =", stylesheet


def loadFeeTables():
    '''
    load the feetables (time consuming)
    '''
    global FEETABLES, CSETYPES, DEFAULT_COURSETYPE

    from openmolar.settings import fee_tables

    LOGGER.debug("loading fee and treatment logic tables")
    FEETABLES = fee_tables.FeeTables()
    CSETYPES = FEETABLES.csetypes
    DEFAULT_COURSETYPE = FEETABLES.default_csetype


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    _test()
