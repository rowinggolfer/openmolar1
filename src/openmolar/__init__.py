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

import os
import sys
import logging
import gettext


class MyFormatter(logging.Formatter):
    '''
    A custom formatter to produce a pretty log
    '''

    def format(self, record):
        filename = "{%s:%s}" % (record.filename, record.lineno)
        return "%s\t %s %s - %s" % (record.levelname,
                                    filename.ljust(25),
                                    record.funcName[:15].ljust(15),
                                    record.getMessage())


if "neil" in os.path.expanduser("~"):
    formatter = MyFormatter()
    FORMAT = ('%(levelname)s\t {%(filename)s:%(lineno)d}\t %(funcName)s'
              '\t- %(message)s')
else:
    FORMAT = '%(levelname)s - %(message)s'
    formatter = logging.Formatter(FORMAT)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
# logging.basicConfig(level = logging.INFO, format=FORMAT)

LOGGER = logging.getLogger("openmolar")
LOGGER.addHandler(stream_handler)

if "-q" in sys.argv:
    LOGGER.setLevel(logging.WARNING)
elif "-v" in sys.argv:
    LOGGER.setLevel(logging.DEBUG)
    LOGGER.warning("verbose logging called by -v flag in sys.argv")
else:
    LOGGER.setLevel(logging.INFO)

LOGGER.debug("running openmolar base module = %s", os.path.dirname(__file__))

try:
    path = os.path.join(os.path.expanduser("~"), ".openmolar", "locale")
    lang1 = gettext.translation("openmolar", localedir=path,
                                languages=['default'])
    lang1.install()
    LOGGER.debug("Installed translation file found in %s", path)
except FileNotFoundError:
    LOGGER.debug("no local translation found")

    lang = os.environ.get("LANG")
    if lang:
        try:
            LOGGER.debug("trying to install your environment language %s", lang)
            lang1 = gettext.translation('openmolar', languages=[lang, ])
            lang1.install()
        except IOError:
            LOGGER.warning("%s not found, using default", lang)
            gettext.install('openmolar')
    else:
        # - on windows.. os.environ.get("LANG") is None
        LOGGER.warning("no language environment found (windows?)")
        gettext.install('openmolar')
