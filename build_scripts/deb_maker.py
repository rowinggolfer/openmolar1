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
this script parses a debian directory, and updates the changelog
command line args determine the behaviour.
--auto  = just alter the changelog with defaults (eg for nightly builds)
'''

import commands
import logging
import optparse
import os
import re
import sys

from PyQt4 import QtGui, QtCore

class DebMakerGui(QtGui.QDialog):
    def __init__(self, changelog, sources, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("Deb Maker")

        label1 = QtGui.QLabel("available sources")
        self.list_widget = QtGui.QListWidget()
        self.list_widget.setMaximumHeight(120)
        for tarball in sources:
            self.list_widget.addItem(tarball)
        self.list_widget.setCurrentRow(0)

        label2 = QtGui.QLabel("changelog")
        self.text_edit = QtGui.QTextEdit()
        self.text_edit.setText(changelog)

        frame = QtGui.QFrame()
        layout = QtGui.QGridLayout(frame)
        layout.addWidget(label1, 0,0)
        layout.addWidget(self.list_widget, 0,1)
        layout.addWidget(label2, 1,0)
        layout.addWidget(self.text_edit, 1,1)

        butbox = QtGui.QDialogButtonBox(self)
        butbox.setStandardButtons(butbox.Ok|butbox.Cancel)

        butbox.accepted.connect(self.accept)
        butbox.rejected.connect(self.reject)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(frame)
        layout.addWidget(butbox)

    def sizeHint(self):
        return QtCore.QSize(600,400)

    @property
    def changelog(self):
        return self.text_edit.toPlainText()

class Parser(optparse.OptionParser):
    def __init__(self):
        optparse.OptionParser.__init__(self,
            prog="deb_maker",
            version="0.1")

        option = self.add_option("-a", "--auto",
                dest = "auto",
                action="store_true", default=False,
                help = "perform default actions with no user input"
                )

        option = self.add_option("-d", "--directory",
                dest="deb_dir",
                help = "debian directory (ie. where your changelog lives)"
                )

        option = self.add_option("-s", "--sources",
                dest="sources_dir",
                help = "sources directory (ie. where your *.tar.gz *.dsc files are)"
                )

        option = self.add_option("-p", "--package-name",
                dest="package",
                help = "package name (eg. openmolar-common)"
                )

def raise_gui(changelog, sources):
    app = QtGui.QApplication(sys.argv)
    dl = DebMakerGui(changelog, sources)
    result = dl.exec_()
    return result, dl.changelog

def new_changelog(package, version, author, package_no=0, dist="__DIST__", urgency="low"):
    return '''%s (%s-%d~%s0) %s; urgency=%s

  * {COMMENTS}

 -- %s  %s
'''% (package, version, package_no, dist, dist, urgency, author, commands.getoutput("date -R"))

def main():
    parser = Parser()
    options, args = parser.parse_args()

    f = open(os.path.join(options.deb_dir, "changelog"))
    changelog = f.read()
    f.close()

    tarballs = []
    print "looking in %s"% options.sources_dir
    for file_ in os.listdir(options.sources_dir):
        if re.match("%s-(.*)\.tar\.gz$"% options.package, file_) :
            tarballs.append(file_)
    tarballs = sorted(tarballs, reverse=True)

    chosen = tarballs[0]
    version = re.match(
        "%s-(.*)\.tar\.gz$"% options.package, chosen).groups()[0]

    new_changes = new_changelog(options.package, version,
        "Neil Wallace <rowinggolfer@googlemail.com>", 0)

    changelog = "%s\n\n%s"% (new_changes, changelog)

    if not options.auto:
        result, changelog = raise_gui(changelog, tarballs)
        if not result:
            sys.exit("User aborted the changelog gui")
    else:
        comments = changelog.replace("{COMMENTS}", "auto build", 1)

    f = open(os.path.join(options.deb_dir, "changelog"), "w")
    f.write(changelog)
    f.close()
	
    logging.info("succesfully written new changelog")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
