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

import logging

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from openmolar.ptModules.course_checker import get_course_checker
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog

LOGGER = logging.getLogger("openmolar")


class CourseConsistencyDialog(ExtendableDialog):

    def __init__(self, serialno, courseno, parent=None):
        ExtendableDialog.__init__(self, parent)
        self.serialno = serialno
        self.courseno = courseno

        header_label = QtWidgets.QLabel("<b>%s %s</b>" % (
            _("Course Daybook Estimate Checker"), self.courseno))
        header_label.setAlignment(QtCore.Qt.AlignCenter)

        self.polling_label = QtWidgets.QLabel(_("Polling Database"))

        self.trt_widget = QtWidgets.QTextBrowser()
        self.day_trt_widget = QtWidgets.QTextBrowser()

        self.insertWidget(header_label)
        self.insertWidget(self.polling_label)

        self.adv_widget = QtWidgets.QLabel(_("No advanced options available"))
        self.add_advanced_widget(self.adv_widget)

        QtCore.QTimer.singleShot(100, self.get_data)

    def advise(self, message):
        QtWidgets.QMessageBox.information(self, _("message"), message)

    def sizeHint(self):
        return QtCore.QSize(800, 600)

    def get_data(self):
        self.course_checker = get_course_checker(self.serialno, self.courseno)
        html1 = self.course_checker.course.to_html()
        html1c = self.course_checker.course.to_html(completed_only = True)
        html2 = self.course_checker.daybook_course.to_html()
        self.polling_label.hide()
        self.insertWidget(QtWidgets.QLabel("course"))
        self.insertWidget(self.trt_widget)
        self.insertWidget(QtWidgets.QLabel("daybook course"))
        self.insertWidget(self.day_trt_widget)

        self.trt_widget.setText(html1)
        self.day_trt_widget.setText(html2)

        # for comparision puporses - dev code!!
        #f = open("/home/neil/course.txt", "w")
        #f.write(html1c)
        #f.close()

        #f = open("/home/neil/day_course.txt", "w")
        #f.write(html2)
        #f.close()

        match = "<b>%s</b>" % ("match!" if html1c == html2 else "differs")
        self.insertWidget(QtWidgets.QLabel(match))

    def update_db(self):
        '''
        apply any edits (should be called if self.exec_() == True)
        '''
        pass
