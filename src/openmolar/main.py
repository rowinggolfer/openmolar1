#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2015 Neil Wallace <neil@openmolar.com>               # #
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
this module puts the "openmolar" modules onto the python path,
and starts the gui
'''

import getopt
import logging
import os
import sys

from openmolar.settings import localsettings

SHORTARGS = "vq"
LONGARGS = [
    "help",
    "version",
    "firstrun",
    "ignore-schema-check",
    "no-dev-login"
]

LOGGER = logging.getLogger("openmolar")

USAGE = '''%s
-q                   \t : %s
-v                   \t : %s

--help               \t : %s
--firstrun           \t : %s
--ignore-schema-check\t : %s
--version            \t : %s
--no-dev-login       \t : %s
'''


def main():
    '''
    main function
    '''
    from openmolar.qt4gui import maingui
    maingui.main()


def usage():
    '''
    called by --help, bad arguments, or no arguments
    simply importing the localsettings will display some system info
    '''
    print USAGE % (
        _("command line options are as follows"),
        _("quiet (minimal logging to console)"),
        _("verbose logging to console (for debugging)"),
        _("show this text"),
        _("offer the firstrun config and demodatabase generation"),
        _("proceed even if client and database versions clash (NOT ADVISABLE!)"),
        _("show the versioning and exit"),
        _("Ignore dev login (advanced)")
    )


def version():
    '''
    show the version on the command line
    '''
    localsettings.showVersion()


def run():
    '''
    the real entry point for the app
    '''

    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], SHORTARGS, LONGARGS)
    except getopt.GetoptError as exc:
        # LOGGER.exception ("Unable to parse command line arguments")
        print "\n%s\n" % exc.msg
        opts = (("--help", ""),)

    # some backward compatibility stuff here...
    if "firstrun" in sys.argv:
        opts.append(("--firstrun", ""))

    chosen_func = main
    for option, arg in opts:
        if option == "--help":
            chosen_func = usage
            break
        if option == "--version":
            chosen_func = version
            break
        if option == "--firstrun":
            localsettings.FORCE_FIRST_RUN = True
        if option == "--ignore-schema-check":
            localsettings.IGNORE_SCHEMA_CHECK = True
            LOGGER.warning("command line args demand no schema check")
    chosen_func()

if __name__ == "__main__":
    # - put "openmolar" on the pyth path and go....
    LOGGER.debug("starting openMolar.... using main.py as __main__")

    def determine_path():
        """Borrowed from wxglade.py"""
        try:
            # could use localsettings.__file__ for non-standard install?
            root = __file__
            if os.path.islink(root):
                root = os.path.realpath(root)
            retarg = os.path.dirname(os.path.abspath(root))
            return retarg
        except:
            LOGGER.exception(
                "There is no __file__ variable.\n"
                "OpenMolar cannot run in this environment")
            sys.exit()

    wkdir = determine_path()
    sys.path.insert(0, os.path.dirname(wkdir))
    run()
