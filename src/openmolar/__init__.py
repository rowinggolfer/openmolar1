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
Whenever openmolar is imported, this module ensures the environment is
sane by initialising gettext and logging.
'''

import gettext
import locale
import logging
import os
import sys
import platform

LOGGER = logging.getLogger("openmolar")

if platform.system() == "Windows":
    DEFAULT_MO_PATH = os.path.join(os.environ.get("APPDATA", ""),
                                   "openmolar", "default.mo")
    SHARE_DIR = os.path.join(os.environ.get("ProgramFiles", ""),
                                 "openmolar")
    L10N_DIR = os.path.join(SHARE_DIR, "locale")
else:
    DEFAULT_MO_PATH = os.path.join(os.path.expanduser("~"),
                                   ".openmolar", "default.mo")
    SHARE_DIR = "/usr/share/openmolar"
    L10N_DIR = "/usr/share/locale"

class MyFormatter(logging.Formatter):
    '''
    A custom formatter to produce a pretty log
    '''

    def format(self, record):
        filename = "{%s:%s}" % (record.filename, record.lineno)
        if record.exc_info:
            exc_info = "\n" + self.formatException(record.exc_info)
        else:
            exc_info = ""
        return "%s\t %s %s - %s%s" % (
            record.levelname,
            filename.ljust(25),
            record.funcName[:15].ljust(15),
            record.getMessage(), exc_info)


def initialise_logging():
    '''
    Customise the logger used by the openmolar application.
    '''
    stream_handler = logging.StreamHandler()
    if "neil" in os.path.expanduser("~"):
        stream_handler.setFormatter(MyFormatter())
    else:
        stream_handler.setFormatter(
            logging.Formatter('%(levelname)s - %(message)s'))

    LOGGER.addHandler(stream_handler)

    if "-q" in sys.argv:
        LOGGER.setLevel(logging.WARNING)
    elif "-v" in sys.argv:
        LOGGER.setLevel(logging.DEBUG)
        LOGGER.warning("verbose logging called by -v flag in sys.argv")
    else:
        LOGGER.setLevel(logging.INFO)


def initialise_translation():
    '''
    Localise the application if possible.
    If a file named "default.mo" is found in ~/.openmolar then that is used.
    Otherwise, gnu gettext searches for the "openmolar" domain
    New with version 0.8.1 - gettext binary files are installed into
    C:\\Program Files\openmolar\locale
    (previously the Python environment was getting polluted)
    '''

    if os.path.isfile(DEFAULT_MO_PATH):
        try:
            with open(DEFAULT_MO_PATH, "rb") as fp:
                translation = gettext.GNUTranslations(fp)
                translation.install()
                LOGGER.info("%s installed as translation", DEFAULT_MO_PATH)
        except:
            LOGGER.exception("The local translation file %s cannot be intalled",
                             DEFAULT_MO_PATH)
    else:
        LOGGER.debug("no local translation found at %s, searching environment",
                     DEFAULT_MO_PATH)


        # defensive coding here as some obscure os (windows??) may give an
        # unexpected result.
        try:
            lang = locale.getdefaultlocale()[0]
        except IndexError:
            LOGGER.debug("locale.getdefaultlocale failed")
            lang = os.environ.get("LANG")

        if lang:
            try:
                LOGGER.debug("trying to install your environment language %s",
                             lang)
                lang1 = gettext.translation('openmolar', localedir=L10N_DIR,
                                            languages=[lang, ])
                lang1.install()
                LOGGER.debug("Language succesfully installed")
            except FileNotFoundError:
                LOGGER.warning("An attempt to install translation %s failed",
                               lang)
        else:
            # - on windows.. os.environ.get("LANG") is None
            LOGGER.warning("no language environment found")


initialise_logging()
LOGGER.debug("Openmolar package location = %s", os.path.dirname(__file__))
initialise_translation()

# finally - make sure _() is present in globals
try:
    _("Find")
except NameError:
    gettext.install('openmolar', localedir=L10N_DIR)
