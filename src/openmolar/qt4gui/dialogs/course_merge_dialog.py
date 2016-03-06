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

import copy
import logging
from PyQt4 import QtGui, QtCore

from openmolar.dbtools import treatment_course
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog

LOGGER = logging.getLogger("openmolar")


class CourseMergeDialog(ExtendableDialog):

    def __init__(self, serialno, courseno1, courseno2, parent=None):
        ExtendableDialog.__init__(self, parent, remove_stretch=True)
        assert courseno1 > courseno2, "courses in wrong order"
        self.serialno = serialno
        self.courseno1 = courseno1
        self.courseno2 = courseno2
        self._merged_course = None

        header_label = QtGui.QLabel(
            "<b>%s %s &amp; %s</b>" % (_("Merge Treatment Courses"),
                                       self.courseno1, self.courseno2))
        header_label.setAlignment(QtCore.Qt.AlignCenter)

        self.polling_label = QtGui.QLabel(_("Polling Database"))

        self.preview_button = QtGui.QPushButton(_("Preview Merged Course"))

        self.courseno1_browser = QtGui.QTextBrowser()
        self.courseno2_browser = QtGui.QTextBrowser()
        self.preview_browser = QtGui.QTextBrowser()

        self.splitter = QtGui.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Vertical)

        self.insertWidget(header_label)
        self.insertWidget(self.polling_label)
        self.insertWidget(self.splitter)

        self.splitter.addWidget(self.courseno1_browser)
        self.splitter.addWidget(self.courseno2_browser)
        self.splitter.addWidget(self.preview_browser)

        self.adv_widget = QtGui.QLabel(_("No advanced options available"))
        self.add_advanced_widget(self.adv_widget)

        QtCore.QTimer.singleShot(100, self.get_data)

    def advise(self, message):
        QtGui.QMessageBox.information(self, _("message"), message)

    def sizeHint(self):
        return QtCore.QSize(600, 600)

    def get_data(self):
        self.tx_course1 = treatment_course.TreatmentCourse(self.serialno,
                                                           self.courseno1)
        self.tx_course2 = treatment_course.TreatmentCourse(self.serialno,
                                                           self.courseno2)
        self.polling_label.hide()
        course1_html = self.tx_course1.to_html()
        course2_html = self.tx_course2.to_html()
        self.courseno1_browser.setHtml(course1_html)
        self.courseno2_browser.setHtml(course2_html)
        if self.tx_course1.examt and self.tx_course2.examt:
            message = _("Courses can't be merged, both have examinations")
        else:
            message = "<h2>%s</h2>%s" % (_("Merged Course Preview"),
                                         self.merged_course.to_html()
                                         )
        self.preview_browser.setText(message)
        sizes = [(course1_html.count("<tr>") + 1) * 300,
                 (course1_html.count("<tr>") + 1) * 300,
                 (message.count("<tr>") + 1) * 300]
        self.splitter.setSizes(sizes)
        LOGGER.debug(sizes)

        self.enableApply(self._merged_course is not None)

    @property
    def _merge_atts(self):
        exclusions = ("courseno", "accd", "cmpd", "examd", "examt")
        for att in treatment_course.CURRTRT_ATTS:
            if att not in exclusions:
                yield att

    @property
    def merged_course(self):
        if self._merged_course is None:
            new_course = copy.deepcopy(self.tx_course2)
            if self.tx_course1.accd < new_course.accd:
                new_course.accd = self.tx_course1.accd
            if (new_course.cmpd is not None or
               self.tx_course1.cmpd > new_course.cmpd):
                new_course.cmpd = self.tx_course1.cmpd
            if (new_course.examd is None or
               (self.tx_course1.examd and
                    self.tx_course1.examd < new_course.examd)):
                new_course.examd = self.tx_course1.examd
            if self.tx_course1.examt > new_course.examt:
                new_course.examt = self.tx_course1.examt
            for att in self._merge_atts:
                value1 = new_course.__dict__[att]
                value2 = self.tx_course1.__dict__[att]
                if value1 in (None, ""):
                    new_course.__dict__[att] = value2
                elif value2 in (None, ""):
                    pass
                else:
                    new_course.__dict__[att] += value2
            self._merged_course = new_course
        return self._merged_course

    def list_hashes(self):
        for tx_course in self.tx_course1, self.tx_course2, self.merged_course:
            print("TX_HASHES for course %s" % tx_course.courseno)
            for tx_hash in tx_course.tx_hashes:
                print(tx_hash)

    def update_db(self):
        '''
        apply any edits (should be called if self.exec_() == True)
        to merge 2 courses, all treatments have to be combined, and placed
        into the oldest course.
        the newestimates table has to have the coursenumber adjusted.
        NOTE - old tx_hashes will not longer be generatable
        by the TreatmentCourseClass
        '''
        trtchanges = ""
        trtvalues = []
        for trt_att in treatment_course.CURRTRT_ATTS:
            if trt_att == "courseno":
                continue
            value = self.merged_course.__dict__[trt_att]
            existing = self.tx_course2.__dict__[trt_att]
            if value != existing:
                trtchanges += '%s = %%s ,' % trt_att
                trtvalues.append(value)
        self.list_hashes()
        if treatment_course.update_course(trtchanges.rstrip(","),
                                          trtvalues,
                                          self.serialno,
                                          self.courseno2
                                          ):
            treatment_course.update_estimate_courseno(self.courseno1,
                                                      self.courseno2)
            treatment_course.delete_course(self.serialno, self.courseno1)


if __name__ == "__main__":

    app = QtGui.QApplication([])
    LOGGER.setLevel(logging.DEBUG)
    dl = CourseMergeDialog(12647, 6879, 2385)
    if dl.exec_():
        dl.update_db()
