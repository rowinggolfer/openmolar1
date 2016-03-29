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

from collections import OrderedDict
from gettext import gettext as _
import logging
import re
import os
import sys
from xml.dom import minidom

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from openmolar.settings import localsettings

from openmolar.qt4gui.feescale_editor.feescale_xml_editor import XMLEditor
from openmolar.qt4gui.feescale_editor.feescale_parser import MessageHandler

from openmolar.qt4gui.phrasebook.phrasebook_model import PhrasesListModel
from openmolar.dbtools.phrasebook import PHRASEBOOKS

LOGGER = logging.getLogger("openmolar")

STYLESHEET = os.path.join(
    localsettings.resources_location, "phrasebook", "phrasebook.xsd")


class ControlPanel(QtWidgets.QListView):
    phrase_selected = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        QtWidgets.QListView.__init__(self, parent)
        self.list_model = PhrasesListModel()

    def set_xml(self, xml):
        self.list_model.set_xml(xml)
        self.setModel(self.list_model)
        self.selectionModel().currentRowChanged.connect(self._phrase_selected)

    def _phrase_selected(self, new_index, old_index):
        self.phrase_selected.emit(new_index)


class PhrasebookEditor(QtWidgets.QMainWindow):
    _checking_files = False
    _known_deleted_parsers = []
    _compare_phrases_dockwidget = None
    search_text = ""
    closed_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.window_title = _("Phrasebook Editor")
        self.setWindowTitle(self.window_title)
        self.loading = True

        statusbar = QtWidgets.QStatusBar()
        self.setStatusBar(statusbar)

        self.control_panel = ControlPanel()
        self.control_panel.phrase_selected.connect(self.find_phrase)

        #: a pointer to the label in the statusbar
        self.cursor_pos_label = QtWidgets.QLabel("Line 0, Column 0")
        statusbar.addPermanentWidget(self.cursor_pos_label)

        self.main_toolbar = QtWidgets.QToolBar()
        self.main_toolbar.setObjectName("Main Toolbar")
        self.main_toolbar.toggleViewAction().setText(_("Toolbar"))

        self.prefs_toolbar = QtWidgets.QToolBar()
        self.prefs_toolbar.setObjectName("Prefs Toolbar")
        self.prefs_toolbar.toggleViewAction().setText(_("Preferences Toolbar"))

        self.addToolBar(QtCore.Qt.TopToolBarArea, self.main_toolbar)
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.prefs_toolbar)

        menu_file = QtWidgets.QMenu(_("&File"), self)
        menu_edit = QtWidgets.QMenu(_("&Edit"), self)
        menu_tools = QtWidgets.QMenu(_("&Tools"), self)

        self.menuBar().addMenu(menu_file)
        self.menuBar().addMenu(menu_edit)
        self.menuBar().addMenu(menu_tools)

        icon = QtGui.QIcon.fromTheme("document-new")
        action_new = QtWidgets.QAction(icon, _("New Phrasebook"), self)
        action_new.setToolTip(_("Create a new clinician phrasebook"))

        icon = QtGui.QIcon(":database.png")
        action_commit = QtWidgets.QAction(icon, _("Commit to Database"), self)
        action_commit.setToolTip(_("Commit changes to database"))

        icon = QtGui.QIcon.fromTheme("document-find")
        action_find = QtWidgets.QAction(icon, _("Find"), self)
        action_find.setShortcut("Ctrl+F")
        action_find.setToolTip(
            _("Search current file for first forward match of entered text"))

        action_find_again = QtWidgets.QAction(icon, _("Find Again"), self)
        action_find_again.setShortcut("Ctrl+G")
        action_find_again.setToolTip(_("Search current file again for text"))

        self.main_toolbar.addAction(action_new)
        self.main_toolbar.addAction(action_commit)

        menu_edit.addAction(action_find)
        menu_edit.addAction(action_find_again)

        menu_file.addAction(action_new)
        menu_file.addAction(action_commit)

        self.tab_widget = QtWidgets.QTabWidget()

        self.phrasebook_parsers = OrderedDict()
        self.text_editors = []

        self.action_refactor = QtWidgets.QAction(_("XML tidy"), self)
        self.action_refactor.triggered.connect(self.refactor)

        self.action_check_parseable = QtWidgets.QAction(
            _("Check Well Formed"), self)
        self.action_check_parseable.triggered.connect(self.check_parseable)

        self.action_check_validity = QtWidgets.QAction(_("Check Validity"), self)
        self.action_check_validity.triggered.connect(self.check_validity)

        menu_tools.addAction(self.action_refactor)
        menu_tools.addAction(self.action_check_parseable)
        menu_tools.addAction(self.action_check_validity)

        self.prefs_toolbar.addAction(self.action_refactor)
        self.prefs_toolbar.addAction(self.action_check_parseable)
        self.prefs_toolbar.addAction(self.action_check_validity)

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self.control_panel)
        splitter.addWidget(self.tab_widget)
        splitter.setSizes([150, 650])
        self.setCentralWidget(splitter)

        action_find.triggered.connect(self.find_text)
        action_find_again.triggered.connect(self.find_again)

        action_commit.triggered.connect(self.apply_changes)
        action_new.triggered.connect(self.new_phrasebook)

        self.tab_widget.currentChanged.connect(self.view_phrasebook)

        QtCore.QTimer.singleShot(1000, self.start_)

    def advise(self, message, importance=0):
        '''
        notify user
        '''
        if importance is 0:
            LOGGER.debug(message)
            m = QtWidgets.QMessageBox(self)
            m.setText(message)
            m.setIcon(m.Information)
            m.setStandardButtons(QtWidgets.QMessageBox.NoButton)
            m.setWindowTitle(_("advisory"))
            m.setModal(False)
            QtCore.QTimer.singleShot(3 * 1000, m.accept)
            m.show()
        elif importance == 1:
            LOGGER.info(message)
            QtWidgets.QMessageBox.information(self, _("Advisory"), message)
        else:
            LOGGER.warning(message)
            QtWidgets.QMessageBox.warning(self, _("Error"), message)

    def sizeHint(self):
        return QtCore.QSize(800, 500)

    def closeEvent(self, event=None):
        '''
        called when application closes.
        '''
        if self.is_dirty:
            message = "<b>%s</b><hr />%s" % (
                _("WARNING - you have unsaved changes!"),
                _("Are you sure you want to quit?"))

            if QtWidgets.QMessageBox.question(
                    self, _("Confirm"),
                    message,
                    QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
                    QtWidgets.QMessageBox.Cancel) == QtWidgets.QMessageBox.Cancel:
                event.ignore()
                return
        self.closed_signal.emit()

    def start_(self):
        self.load_phrasebooks()
        self.view_phrasebook(0)

    def load_phrasebooks(self):
        self.loading = True
        while self.tab_widget.count():
            self.tab_widget.removeTab(0)
        for editor in self.text_editors:
            editor.setParent(None)
        self.text_editors = []
        for book in PHRASEBOOKS.get_all_books():
            editor = XMLEditor(self)
            editor.editor_settings()
            editor.setText(book.xml)
            editor.db_index = book.ix
            editor.textChanged.connect(self.text_changed)
            editor.cursorPositionChanged.connect(self.cursor_position_changed)

            if book.ix == 0:
                title = _("Global Phrasebook")
            else:
                title = localsettings.ops[book.ix]
            self.text_editors.append(editor)

            self.tab_widget.addTab(editor, title)

        self.loading = False

    def view_phrasebook(self, ix=0):
        LOGGER.debug("View phrasebook %s" % ix)
        while self.loading:
            QtCore.QTimer.singleShot(1000, self.view_phrasebook)
            return
        if len(self.text_editors) > 0:
            self.control_panel.set_xml(self.text_editors[ix].text)
            self.setWindowTitle(
                "%s - %s" % (self.window_title, ix))
            self.update_index()
        else:
            QtWidgets.QMessageBox.information(
                self, _("Information"),
                _("You appear to have no phrasebooks "
                  "installed in your database"))

    def update_index(self):
        self.control_panel.set_xml(self.text)

    @property
    def text_edit(self):
        return self.text_editors[self.tab_widget.currentIndex()]

    @property
    def text(self):
        return str(self.text_edit.text())

    def refactor(self):
        if not self.check_parseable(show_message=False):
            return
        xml = re.sub(">[\s]*<", "><", self.text)
        dom = minidom.parseString(xml)

        # don't use setText here that updates orig_text and is_dirty won't work
        self.text_edit.update_text(dom.toprettyxml())

    def check_parseable(self, action=None, show_message=True):
        try:
            minidom.parseString(self.text)
            if show_message:
                self.advise(_("Phrasebook is well formed"), 1)
            return True
        except Exception as exc:
            self.advise("<b>%s</b><hr />%s" % (
                _("Phrasebook is not well formed"), exc.message), 2)
        return False

    def check_validity(self):
        result, message = self.check_xml_validity(self.text)
        if result:
            self.advise(_("Phrasebook is valid"), 1)
        else:
            self.advise(message.last_error, 1)

    def check_xml_validity(self, xml):
        message_handler = MessageHandler()

        LOGGER.debug("checking phrasebook xml against %s", STYLESHEET)
        f = QtCore.QFile(STYLESHEET)
        f.open(QtCore.QIODevice.ReadOnly)
        schema = QXmlSchema()
        schema.load(f)

        validator = QXmlSchemaValidator(schema)
        validator.setMessageHandler(message_handler)
        result = validator.validate(self.text)

        return result, message_handler

    def find_phrase(self, index):
        phrase_count = 0
        for lineno, line in enumerate(self.text.split("\n")):
            if phrase_count == index.row() + 1:
                self.text_edit.setFocus(True)
                self.text_edit.setFirstVisibleLine(lineno - 2)
                self.text_edit.setCursorPosition(lineno - 1, 0)
                self.text_edit.ensureCursorVisible()
                break

            if "<section"in line:
                phrase_count += 1
        if self._compare_phrases_dockwidget:
            id = self.list_view.model().id_from_index(index)
            self.compare_phrase(id)

    def find_text(self):
        self.search_text, result = QtWidgets.QInputDialog.getText(
            self, _("Find Text"),
            _("Please enter the text you wish to search for"),
            QtWidgets.QLineEdit.Normal, self.search_text)
        if result:
            self.find_again()

    def find_again(self):
        if not self.text_edit.findFirst(
                self.search_text, True, True, True, True):
            self.advise("'%s' %s" % (self.search_text, _("not found")))

    def new_phrasebook(self):
        offer_list = []
        for ix in localsettings.activedent_ixs + localsettings.activehyg_ixs:
            if not PHRASEBOOKS.has_book(ix):
                offer_list.append(localsettings.ops[ix])
        if offer_list == []:
            self.advise(_("Everyone has a phrasebook already!"), 2)
            return
        dl = QtWidgets.QInputDialog(self)
        choice, result = dl.getItem(
            self, _("Choose"),
            _("A phrasebook for which clinician?"), sorted(offer_list))
        if result:
            ix = localsettings.ops_reverse[str(choice)]
            PHRASEBOOKS.create_book(ix)
            self.load_phrasebooks()

    def apply_changes(self):
        if QtWidgets.QMessageBox.question(
                self, _("confirm"),
                _("commit all local files to database?"),
                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel
                ) == QtWidgets.QMessageBox.Ok:
            no_ = 0
            for te in self.text_editors:
                if not te.is_dirty:
                    continue
                new_xml = te.text()
                result, message = self.check_xml_validity(new_xml)
                if not result:
                    self.advise("%s %s %s" % (_("Phrasebook"), te.db_index,
                                              _("is not valid")), 2)
                    continue
                result = PHRASEBOOKS.update_database(new_xml, te.db_index)
                if result:
                    te.setText(new_xml)
                    no_ += 1
            self.advise("%s %d %s" % (_("Updated"), no_, _("Books")), 1)

    def cursor_position_changed(self, row, col):
        self.cursor_pos_label.setText("Line %d, Column %d" % (row + 1, col))

    def text_changed(self):
        new_text = self.text_edit.text()
        if self.text_edit.orig_text.count("\n") != new_text.count("\n"):
            self.update_index()

    @property
    def is_dirty(self):
        try:
            for te in self.text_editors:
                if te.is_dirty:
                    LOGGER.debug("%s is dirty" % te)
                    return True
            return False
        except:
            LOGGER.exception("property_exception")


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    localsettings.initiate()
    app = QtWidgets.QApplication(sys.argv)
    mw = PhrasebookEditor()
    mw.show()
    app.exec_()
