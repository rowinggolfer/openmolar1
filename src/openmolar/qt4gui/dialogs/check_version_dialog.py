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

import configparser
from datetime import date, timedelta
import logging
import re
import os
import socket
import urllib.request
import urllib.error
import urllib.parse

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from openmolar.settings import localsettings
from openmolar.qt4gui.customwidgets.warning_label import WarningLabel
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog

LOGGER = logging.getLogger("openmolar")

LOOKUP_URL = "https://openmolar.com/om1/get_version"
INFORMATION_URL = "https://openmolar.com/om1"

HEADERS = {
    'User-Agent': 'openmolar%s' % localsettings.VERSION,
    'Accept': 'text/plain',
    'Accept-Charset': 'utf-8',
    'Accept-Encoding': 'none',
    'Connection': 'close'}

MESSAGE = '''<p>%s <b>%s</b></p>
<hr /><p>%s <b>%%s</b> - %s %%s</p><p><em>%%s</em></p><hr />
<p>%s <a href="%s"> %s </a></p>''' % (
    _("This application is at version"),
    localsettings.VERSION,
    _("The latest release is"),
    _("Released on"),
    _("For more information, please visit"),
    INFORMATION_URL,
    _("The OpenMolar Website"))

CONFIG_PATH = os.path.join(localsettings.LOCALFILEDIRECTORY, "updates.conf")


def parse_isodate(isodate):
    '''
    take a date in iso format "YYYY-MM-DD" and return as a python date object
    return None if no match.
    '''
    LOGGER.debug("attempting to get a date from %s", isodate)
    try:
        m = re.match(r"(\d+)-(\d+)-(\d+)", isodate)
        if m:
            return date(int(m.groups()[0]), int(m.groups()[1]),
                        int(m.groups()[2]))
    except:
        LOGGER.exception("unable to convert %s to a date", isodate)
    return None


class Options(object):
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
    NEVER = 4
    DEFAULT = DAILY

    READABLE_VALUES = {DAILY: "DAILY",
                       WEEKLY: "WEEKLY",
                       MONTHLY: "MONTHLY",
                       NEVER: "NEVER"}

    checked_today = False


class MyConfigParser(configparser.ConfigParser, Options):

    user_chosen_option = None

    def __init__(self):
        '''
        read the local config file and see if user has specified preferences
        as to when checking should take place.
        '''
        configparser.ConfigParser.__init__(self)
        self.read(CONFIG_PATH)
        if "UPDATE" not in self.sections():
            self.write_config()

    @property
    def update_option_value(self):
        '''
        return a human readable (in english!) of the chosen update frequency
        '''
        if self.user_chosen_option:
            return self.READABLE_VALUES.get(self.user_chosen_option, "DAILY")
        return self.READABLE_VALUES.get(self.update_option, "DAILY")

    @property
    def update_option(self):
        try:
            option = self.get("UPDATE", "OPTION")
            for key, value in self.READABLE_VALUES.items():
                if value == option:
                    return key
        except configparser.NoOptionError:
            pass
        except ValueError:
            pass
        return self.DEFAULT

    @property
    def last_check_date(self):
        if self.update_option != self.NEVER:
            try:
                last_check = self.get("UPDATE", "LAST_CHECK")
                return parse_isodate(last_check)
            except configparser.NoOptionError:
                pass
        return date(2000, 1, 1)

    def write_config(self):
        LOGGER.debug("writing config")
        self.clear()
        self.add_section("UPDATE")
        self.set("UPDATE", "OPTION", self.update_option_value)
        if self.checked_today:
            self.set("UPDATE", "LAST_CHECK", date.today().isoformat())
        else:
            self.set("UPDATE", "LAST_CHECK", self.last_check_date.isoformat())
        with open(CONFIG_PATH, "w") as f:
            self.write(f)
            f.close()


class OptionsWidget(QtWidgets.QWidget, Options):
    '''
    A widget for selecting user preferences on checking for updates.
    '''

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.rb1 = QtWidgets.QRadioButton(_("Check for updates daily"))
        self.rb2 = QtWidgets.QRadioButton(_("Check for updates weekly"))
        self.rb3 = QtWidgets.QRadioButton(_("Check for updates monthly"))
        self.rb4 = QtWidgets.QRadioButton(_("Never check for updates"))

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.addWidget(self.rb1)
        layout.addWidget(self.rb2)
        layout.addWidget(self.rb3)
        layout.addWidget(self.rb4)
        self.set_chosen_option()

    def set_chosen_option(self, option=None):
        if option is None:
            option = self.DEFAULT
        self.rb1.setChecked(option == self.DAILY)
        self.rb2.setChecked(option == self.WEEKLY)
        self.rb3.setChecked(option == self.MONTHLY)
        self.rb4.setChecked(option == self.NEVER)

    @property
    def chosen_option(self):
        if self.rb1.isChecked():
            return self.DAILY
        if self.rb2.isChecked():
            return self.WEEKLY
        if self.rb3.isChecked():
            return self.MONTHLY
        if self.rb4.isChecked():
            return self.NEVER


class CheckVersionDialog(ExtendableDialog, Options):
    '''
    A dialog which informs the user of any updates to the openmolar application
    '''
    result = None
    _new_version = None
    _next_check_date = None
    header_text = _("A newer version of OpenMolar is available")

    def __init__(self, force_check=False, parent=None):
        ExtendableDialog.__init__(self, parent)
        self.config = MyConfigParser()

        self.worth_executing = (self.version_lookup(force_check) and (
            self.update_available or force_check))

        if self.worth_executing:
            header_label = WarningLabel(self.header_text)
            header_label.label.setOpenExternalLinks(True)
            details_label = QtWidgets.QLabel(MESSAGE % (self.new_version))
            details_label.setAlignment(QtCore.Qt.AlignCenter)

            self.insertWidget(header_label)
            self.insertWidget(details_label)

            self.cancel_but.hide()
            self.apply_but.setText(_("OK"))
            self.enableApply()

            self.options_widget = OptionsWidget(self)
            self.options_widget.set_chosen_option(self.config.update_option)
            self.set_advanced_but_text(_("Options"))
            self.add_advanced_widget(self.options_widget)

    def version_lookup(self, force_check):
        '''
        poll the server for a simd for a postcode
        '''
        LOGGER.debug("version_lookup")
        if self.config.update_option == self.NEVER and not force_check:
            return False
        if self.config.update_option == self.MONTHLY:
            delta = timedelta(days=30)
        elif self.config.update_option == self.WEEKLY:
            delta = timedelta(days=7)
        else:  # DAILY
            delta = timedelta(days=1)
        if force_check:
            LOGGER.warning("Check Version Dialog Called with force=True")
        elif self.config.last_check_date + delta > date.today():
            LOGGER.debug("update check not due yet")
            return False
        LOGGER.info("polling for updates")
        QtWidgets.QApplication.instance().processEvents()
        try:
            self.config.checked_today = True
            req = urllib.request.Request(LOOKUP_URL, headers=HEADERS)
            response = urllib.request.urlopen(req, timeout=20)
            self.result = response.read().decode("utf8")
            LOGGER.info("\n".join(("UPSTREAM VERSION:",
                                   "- -" * 30,
                                   self.result,
                                   "- -" * 30)))
        except urllib.error.URLError:
            LOGGER.error("url error polling openmolar website?")
            self.result = _("Error polling website")
            return False
        except socket.timeout:
            LOGGER.error("timeout error polling openmolar website?")
            self.result = _("Timeout polling website")
            return False
        except Exception:
            LOGGER.exception("unknown error getting response from website")
        return True

    @property
    def update_available(self):
        '''
        a boolean to lookup whether a new version is available.
        '''
        LOGGER.debug("getting property update_available")
        try:
            if self.new_version[0] > localsettings.VERSION:
                LOGGER.info("There is a newer version available upstream")
                return True
            else:
                self.header_text = _(
                    "You are running the latest version - thankyou")
                LOGGER.info("You are running the latest version - thankyou")
                return False
        except:
            LOGGER.exception("unknown error getting update available")
            return False

    @property
    def new_version(self):
        if self._new_version is None:
            scp = configparser.ConfigParser()
            scp.read_string(self.result)
            version, release_date, message = "", None, ""
            try:
                try:
                    version = scp.get("RELEASE", "VERSION")
                except configparser.NoOptionError:
                    pass
                try:
                    release_date_string = scp.get("RELEASE", "DATE")
                    m = re.match(r"(\d+),(\d+),(\d+)", release_date_string)
                    if m:
                        release_date = date(int(m.groups()[0]),
                                            int(m.groups()[1]),
                                            int(m.groups()[2]))
                    else:
                        LOGGER.warning("release date not in form 2016,03,09")
                except configparser.NoOptionError:
                    pass
                except ValueError:  # this will fire if a bad date is passed.
                    logging.exception("error parsing date field")
                try:
                    message = scp.get("RELEASE", "MESSAGE")
                except configparser.NoOptionError:
                    pass
            except configparser.NoSectionError:
                LOGGER.warning("unable to parse result of version checking")
            except configparser.MissingSectionHeaderError:
                pass
            self._new_version = (version,
                                 localsettings.formatDate(release_date),
                                 message.replace("\n", "<br />"))
        return self._new_version

    def exec_(self):
        if self.worth_executing:
            if ExtendableDialog.exec_(self):
                self.config.user_chosen_option = \
                    self.options_widget.chosen_option
                self.config.write_config()
            return True
        return False


class ThreadedCheckVersion(QtCore.QThread):

    def __init__(self, parent=None):
        self.parent = parent
        QtCore.QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        dl = CheckVersionDialog(False, self.parent)
        dl.exec_()


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    app = QtWidgets.QApplication([])
    thread = ThreadedCheckVersion()
    thread.run()
