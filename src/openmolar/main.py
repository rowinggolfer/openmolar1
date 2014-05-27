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

'''
this module puts the "openmolar" modules onto the python path,
and starts the gui
'''

import getopt
import logging
import sys
import os
import hashlib

from xml.dom import minidom

from openmolar.settings import localsettings

SHORTARGS = "v"
LONGARGS = ["help", "version", "setup", "firstrun", "user=", "db=", "port=",
            "ignore-schema-check"]

LOGGER = logging.getLogger("openmolar")

USAGE = '''%s
--help               \t : %s
--firstrun           \t : %s
--ignore-schema-check\t : %s
--setup              \t : %s
--version            \t : %s
'''

def first_run():
    import first_run
    if first_run.run():
        main()
    else:
        sys.exit()

def main():
    '''
    main function
    '''
    if os.path.exists(localsettings.global_cflocation):
        localsettings.cflocation = localsettings.global_cflocation
        cf_Found = True
    else:
        cf_found = os.path.exists(localsettings.cflocation)
    if cf_found:
        from openmolar.qt4gui import maingui
        maingui.main()
    else:
        first_run()

def setup():
    '''
    run the setup gui, which allows customisation of the app
    '''
    from openmolar.qt4gui.tools import new_setup
    new_setup.main(sys.argv)

def usage():
    '''
    called by --help, bad arguments, or no arguments
    simply importing the localsettings will display some system info
    '''
    print USAGE % (
    _("command line options are as follows"),
    _("show this text"),
    _("offer the firstrun config and demodatabase generation"),
    _("proceed even if client and database versions clash (NOT ADVISABLE!)"),
    _("takes you to the admin page"),
    _("show the versioning and exit")
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
        LOGGER.exception ("Unable to parse command line arguments")
        opts = (("--help", ""),)

    # some backward compatibility stuff here...
    if "setup" in sys.argv:
        opts.append(("--setup", ""))
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
        if option == "--setup":
            LOGGER.info("setup called by command line args")
            chosen_func = setup
            break
        if option == "--firstrun":
            chosen_func = first_run
            break
        if option == "--ignore-schema-check":
            localsettings.IGNORE_SCHEMA_CHECK = True
            LOGGER.warning("command line args demand no schema check")
    chosen_func()

if __name__ == "__main__":
    #-- put "openmolar" on the pyth path and go....
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
