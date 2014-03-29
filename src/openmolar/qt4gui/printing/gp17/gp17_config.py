#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011, Neil Wallace <rowinggolfer@googlemail.com>               ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

'''
Provides a Class for printing the GP17-1(Scotland) NHS form (back side)
'''
import ConfigParser
import os
from openmolar.settings import localsettings

CONF_PATH = os.path.join(localsettings.localFileDirectory, "gp17.conf")

SECTIONS = ("gp17Front", "gp17iFront", "gp17iBack")

class GP17Config(ConfigParser.ConfigParser):
    def __init__(self):
        ConfigParser.ConfigParser.__init__(self)
        self.read_conf()
        for section in SECTIONS:
            try:
                self.add_section(section)
            except ConfigParser.DuplicateSectionError:
                pass

    def read_conf(self):
        self.read([CONF_PATH])

    @property
    def OFFSET_LEFT(self):
        try:
            return int(self.get("gp17Front", "left"))
        except ConfigParser.NoOptionError:
            return 0

    @property
    def OFFSET_TOP(self):
        try:
            return int(self.get("gp17Front", "top"))
        except ConfigParser.NoOptionError:
            return 0

    @property
    def SCALE_X(self):
        try:
            return float(self.get("gp17Front", "scale_x"))
        except ConfigParser.NoOptionError:
            return 1.0

    @property
    def SCALE_Y(self):
        try:
            return float(self.get("gp17Front", "scale_y"))
        except ConfigParser.NoOptionError:
            return 1.0

    @property
    def GP17i_OFFSET_LEFT(self):
        try:
            return int(self.get("gp17iFront", "left"))
        except ConfigParser.NoOptionError:
            return 0

    @property
    def GP17i_OFFSET_TOP(self):
        try:
            return int(self.get("gp17iFront", "top"))
        except ConfigParser.NoOptionError:
            return 0

    @property
    def GP17i_SCALE_X(self):
        try:
            return float(self.get("gp17iFront", "scale_x"))
        except ConfigParser.NoOptionError:
            return 1.0

    @property
    def GP17i_SCALE_Y(self):
        try:
            return float(self.get("gp17iFront", "scale_y"))
        except ConfigParser.NoOptionError:
            return 1.0

    @property
    def GP17iback_OFFSET_LEFT(self):
        try:
            return int(self.get("gp17iBack", "left"))
        except ConfigParser.NoOptionError:
            return 0

    @property
    def GP17iback_OFFSET_TOP(self):
        try:
            return int(self.get("gp17iBack", "top"))
        except ConfigParser.NoOptionError:
            return 0

    @property
    def GP17iback_SCALE_X(self):
        try:
            return float(self.get("gp17iBack", "scale_x"))
        except ConfigParser.NoOptionError:
            return 1.0

    @property
    def GP17iback_SCALE_Y(self):
        try:
            return float(self.get("gp17iBack", "scale_y"))
        except ConfigParser.NoOptionError:
            return 1.0


    def save_config(self):
        self.set("gp17Front", "left", self.OFFSET_LEFT)
        self.set("gp17Front", "top", self.OFFSET_TOP)
        self.set("gp17Front", "scale_x", self.SCALE_X)
        self.set("gp17Front", "scale_y", self.SCALE_Y)

        self.set("gp17iFront", "left", self.GP17i_OFFSET_LEFT)
        self.set("gp17iFront", "top", self.GP17i_OFFSET_TOP)
        self.set("gp17iFront", "scale_x", self.GP17i_SCALE_X)
        self.set("gp17iFront", "scale_y", self.GP17i_SCALE_Y)

        self.set("gp17iBack", "left", self.GP17iback_OFFSET_LEFT)
        self.set("gp17iBack", "top", self.GP17iback_OFFSET_TOP)
        self.set("gp17iBack", "scale_x", self.GP17iback_SCALE_X)
        self.set("gp17iBack", "scale_y", self.GP17iback_SCALE_Y)

        f = open(CONF_PATH, "w")
        self.write(f)
        f.close()

gp17config = GP17Config()

if __name__ == "__main__":
    gp17config.save_config()
