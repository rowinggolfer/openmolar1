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
from datetime import date
from datetime import timedelta
import logging
import re
import os

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtNetwork

from openmolar.settings import localsettings
from openmolar.qt4gui.customwidgets.warning_label import WarningLabel
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog

LOGGER = logging.getLogger("openmolar")

LOOKUP_URL = "https://openmolar.com/om1/get_version"

INFORMATION_URL = "https://openmolar.com/"

USER_AGENT_HEADER = 'openmolar%s' % localsettings.VERSION

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
    ALWAYS = 0
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
    NEVER = 4
    DEFAULT = ALWAYS

    READABLE_VALUES = {ALWAYS: "ALWAYS",
                       DAILY: "DAILY",
                       WEEKLY: "WEEKLY",
                       MONTHLY: "MONTHLY",
                       NEVER: "NEVER"}

    checked_today = False


class DataFetcher(QtCore.QObject):
    finished_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._access_manager = QtNetwork.QNetworkAccessManager()
        self._data = None
        self._access_manager.finished.connect(self._access_manager_finished)
        self.timeout_timer = QtCore.QTimer()
        self.timeout_timer.timeout.connect(self.timeout)
        self.timeout_timer.start(20000)

    def _access_manager_finished(self, reply):
        self.timeout_timer.stop()
        self._data = reply.readAll()
        assert isinstance(self._data, QtCore.QByteArray)
        self.finished_signal.emit()

    def get_webdata(self):
        request = QtNetwork.QNetworkRequest(QtCore.QUrl(LOOKUP_URL))
        request.setHeader(QtNetwork.QNetworkRequest.UserAgentHeader,
                          USER_AGENT_HEADER)
        self._access_manager.get(request)

    def result(self):
        try:
            result = self._data.data().decode("utf8")
            return result if result else None
        except:
            return None

    def timeout(self):
        self.timeout_timer.stop()
        self.finished_signal.emit()


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
            return self.READABLE_VALUES.get(self.user_chosen_option, "ALWAYS")
        return self.READABLE_VALUES.get(self.update_option, "ALWAYS")

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
        self.rb0 = QtWidgets.QRadioButton(_("Check for updates with every run"))
        self.rb1 = QtWidgets.QRadioButton(_("Check for updates daily"))
        self.rb2 = QtWidgets.QRadioButton(_("Check for updates weekly"))
        self.rb3 = QtWidgets.QRadioButton(_("Check for updates monthly"))
        self.rb4 = QtWidgets.QRadioButton(_("Never check for updates"))

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.addWidget(self.rb0)
        layout.addWidget(self.rb1)
        layout.addWidget(self.rb2)
        layout.addWidget(self.rb3)
        layout.addWidget(self.rb4)
        self.set_chosen_option()

    def set_chosen_option(self, option=None):
        if option is None:
            option = self.DEFAULT
        self.rb0.setChecked(option == self.ALWAYS)
        self.rb1.setChecked(option == self.DAILY)
        self.rb2.setChecked(option == self.WEEKLY)
        self.rb3.setChecked(option == self.MONTHLY)
        self.rb4.setChecked(option == self.NEVER)

    @property
    def chosen_option(self):
        if self.rb0.isChecked():
            return self.ALWAYS
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
    There are 2 ways of calling this dialog.
    exec_() = show the dialog before polling the wesbite for releases
    background_exec() = only show the result if there is a new version.
    '''
    result = None
    _new_version = None
    _next_check_date = None
    polling = False

    def __init__(self, parent=None):
        LOGGER.debug("initiating CheckVersionDialog")
        ExtendableDialog.__init__(self, parent)
        self.data_fetcher = DataFetcher(parent)
        self.config = MyConfigParser()

    def add_widgets(self):
        self.header_label = WarningLabel(
            _("Checking for updates.... please wait."))
        self.result_label = QtWidgets.QLabel("")
        self.result_label.setAlignment(QtCore.Qt.AlignCenter)
        self.result_label.setOpenExternalLinks(True)

        self.insertWidget(self.header_label)
        self.insertWidget(self.result_label)

        self.cancel_but.hide()
        self.apply_but.setText(_("OK"))
        self.enableApply()

        self.options_widget = OptionsWidget(self)
        self.options_widget.set_chosen_option(self.config.update_option)
        self.set_advanced_but_text(_("Options"))
        self.add_advanced_widget(self.options_widget)

    def show_result(self):
        LOGGER.debug("CheckVersionDialog show result")
        self.result = self.data_fetcher.result()
        if self.result is None:
            self.result_label.setText(
                "%s<br /><a href='%s'>%s</a>" % (_("Unable to connect to"),
                                                 INFORMATION_URL,
                                                 INFORMATION_URL))
            return
        if self.update_available:
            header_text = _("A newer version of OpenMolar is available")
            self.header_label.label.setStyleSheet("color: red")
        else:
            header_text = _("You are running the latest version - thankyou")

        self.header_label.setText(header_text)
        self.result_label.setText(MESSAGE % (self.new_version))

    def lookup_due(self):
        '''
        check the config file for user preferences on update check
        '''
        LOGGER.debug("checking user preferences for application update check")
        if self.config.update_option == self.NEVER:
            return False
        if self.config.update_option == self.MONTHLY:
            delta = timedelta(days=30)
        elif self.config.update_option == self.WEEKLY:
            delta = timedelta(days=7)
        elif self.config.update_option == self.DAILY:
            delta = timedelta(days=1)
        else:
            delta = timedelta(days=0)
        if self.config.last_check_date + delta > date.today():
            LOGGER.debug("update check not due yet")
            return False
        return True

    def hit_website(self):
        if not self.polling:
            LOGGER.info("polling website for latest release")
            self.polling = True
            self.data_fetcher.get_webdata()

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
                LOGGER.info("You are running the latest version - thankyou")
                return False
        except:
            LOGGER.exception("unknown error getting update available "
                             "perhaps the website returned garbage???")
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
                        self.checked_today = True
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

    def background_exec(self):
        if self.lookup_due():
            self.data_fetcher.finished_signal.connect(self.exec_)
            self.hit_website()

    def exec_(self):
        LOGGER.debug("exec_ called by %s", self.sender())
        self.add_widgets()
        if self.sender() == self.data_fetcher:
            self.show_result()
            # lookup has been performed discreetly, only bother the user if
            # there is an update available
            if not self.update_available:
                return False
        else:
            self.data_fetcher.finished_signal.connect(self.show_result)
            QtCore.QTimer.singleShot(5000, self.hit_website)
        if ExtendableDialog.exec_(self):
            self.config.user_chosen_option = self.options_widget.chosen_option
            self.config.checked_today = self.checked_today
            self.config.write_config()


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    app = QtWidgets.QApplication([])
    dl = CheckVersionDialog()
    if True:
        dl.exec_()
    else:
        dl.background_exec()
        app.exec_()
