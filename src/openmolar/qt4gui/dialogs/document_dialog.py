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
import os

from PyQt5 import QtCore, QtWidgets

from openmolar.settings import localsettings, urls
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog

from xml.dom import minidom

LOGGER = logging.getLogger("openmolar")


def _null_func():
    return None


class _FileListWidget(QtWidgets.QScrollArea):

    def __init__(self, files, parent=None):
        assert files != [], "no files passed to FileListWidget"
        QtWidgets.QScrollArea.__init__(self, parent)
        self.files = files
        self.labels = files
        self.radio_buts = []
        self.layout_widgets()
        self.radio_buts[0].setChecked(True)

    def layout_widgets(self):
        frame = QtWidgets.QFrame(self)
        layout = QtWidgets.QVBoxLayout(frame)
        self.setWidget(frame)
        self.setWidgetResizable(True)
        for label in self.labels:
            rb = QtWidgets.QRadioButton(label)
            layout.addWidget(rb)
            self.radio_buts.append(rb)

    def selected_file(self):
        for i, rb in enumerate(self.radio_buts):
            if rb.isChecked():
                return self.files[i]

    def sizeHint(self):
        return QtCore.QSize(200, 400)


class _LabelledFileListWidget(_FileListWidget):

    def __init__(self, nodelist, parent=None):
        QtWidgets.QScrollArea.__init__(self, parent)
        self.files = []
        self.labels = []
        self.radio_buts = []
        for doc_node in nodelist:
            self.files.append(doc_node.getAttribute("filename"))
            self.labels.append(doc_node.getAttribute("title"))
        assert self.files != [], "no files passed to _LabelledFileListWidget"
        self.layout_widgets()


class DocumentDialog(ExtendableDialog):

    def __init__(self, parent=None):
        ExtendableDialog.__init__(self, parent, remove_stretch=True)

        title = _("Openmolar Documents Dialog")
        self.setWindowTitle(title)
        label = QtWidgets.QLabel(
            "<b>%s</b>" %
            _("Please choose a document to open"))
        label.setAlignment(QtCore.Qt.AlignCenter)

        self.chosen_document = None

        message = '<p>%s<br /><a href="%s">%s</a></p>' % (
            _("For help configuring this feature, see"),
            urls.DOCUMENT_HELP, urls.DOCUMENT_HELP)

        advanced_label = QtWidgets.QLabel(message)
        advanced_label.setOpenExternalLinks(True)
        self.add_advanced_widget(advanced_label)

        files = os.listdir(localsettings.DOCS_DIRECTORY)

        if files == []:
            widg = QtWidgets.QLabel("<p>%s %s</p><hr />%s" % (
                                _("You have no documents stored in"),
                                localsettings.DOCS_DIRECTORY, message))
            widg.setAlignment(QtCore.Qt.AlignCenter)
            widg.setOpenExternalLinks(True)
            widg.selected_file = _null_func

        elif "docs.xml" in files:
            dom = None
            try:
                control_f = os.path.join(
                    localsettings.DOCS_DIRECTORY, "docs.xml")
                dom = minidom.parse(control_f)
                doc_node = dom.getElementsByTagName("documents")[0]
                widg = QtWidgets.QTabWidget()
                for group in doc_node.getElementsByTagName("group"):
                    docs = group.getElementsByTagName("document")
                    group_widg = _LabelledFileListWidget(docs)
                    tab = widg.addTab(
                        group_widg,
                        group.getAttribute("heading"))
                    group_widg.radio_buts[0].setChecked(True)
                widg.selected_file = widg.currentWidget().selected_file
            except:
                LOGGER.exception("unable to parse '%s'" % control_f)
                widg = QtWidgets.QLabel(_("docs.xml is not parseable"))

        else:
            # self.remove_spacer()
            widg = _FileListWidget(files)

        self.enableApply(bool(widg.selected_file()))
        self.insertWidget(label)
        self.insertWidget(widg)
        self._widg = widg

    @property
    def widg(self):
        try:
            return self._widg.currentWidget()
        except AttributeError:
            return self._widg

    def sizeHint(self):
        return QtCore.QSize(400, 350)

    def _open_document(self):
        '''
        open the chosen document
        '''
        doc = self.widg.selected_file()
        if doc is None:
            return
        try:
            doc = os.path.abspath(
                os.path.join(localsettings.DOCS_DIRECTORY, doc))
            LOGGER.info("opening %s" % doc)
            localsettings.openPDF(doc)
        except Exception as exc:
            message = _("Error opening PDF file")
            LOGGER.exception(message)
            self.parent().advise(message, 2)

    def exec_(self):
        if ExtendableDialog.exec_(self):
            self._open_document()
            return True
        return False


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    def advise(message, severity):
        QtWidgets.QMessageBox.information(dl, "message", message)

    mw = QtWidgets.QWidget()
    dl = DocumentDialog(mw)
    dl.exec_()
