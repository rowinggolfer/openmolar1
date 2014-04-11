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

import os
import sys
import logging
import gettext

if "neil" in os.path.expanduser("~"):
    FORMAT = \
        '%(levelname)s {%(filename)s:%(lineno)d} %(funcName)s  - %(message)s'
else:
    FORMAT = '%(levelname)s - %(message)s'

stream_handler = logging.StreamHandler()
formatter = logging.Formatter(FORMAT)
stream_handler.setFormatter(formatter)
# logging.basicConfig(level = logging.INFO, format=FORMAT)

LOGGER = logging.getLogger("openmolar")
LOGGER.addHandler(stream_handler)

if "-q" in sys.argv:
    LOGGER.setLevel(logging.WARNING)
elif "-v" in sys.argv:
    LOGGER.setLevel(logging.DEBUG)
else:
    LOGGER.setLevel(logging.INFO)

LOGGER.debug("running openmolar base module = %s" % os.path.dirname(__file__))

lang = os.environ.get("LANG")
if lang:
    try:
        LOGGER.debug("trying to install your environment language %s" % lang)
        lang1 = gettext.translation('openmolar', languages=[lang, ])
        lang1.install(unicode=True)
    except IOError:
        LOGGER.warning("%s not found, using default" % lang)
        gettext.install('openmolar', unicode=True)
else:
    #-- on windows.. os.environ.get("LANG") is None
    LOGGER.warning("no language environment found (windows?)")
    gettext.install('openmolar', unicode=True)
