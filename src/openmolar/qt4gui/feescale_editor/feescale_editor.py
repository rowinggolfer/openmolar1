#! /usr/bin/python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2013, Neil Wallace <neil@openmolar.com>                        ##
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


import logging
import re
import os
import sys
from gettext import gettext as _
from xml.dom import minidom
from collections import OrderedDict

from PyQt4 import QtCore, QtGui, Qsci
from openmolar.qt4gui import resources_rc

LOGGER = logging.getLogger("openmolar")

from feescale_parser import FeescaleParser
from feescale_list_model import FeescaleListModel
from openmolar.dbtools.feescales import feescale_handler, FEESCALE_DIR

class XMLEditor(Qsci.QsciScintilla):
    editing_finished = QtCore.pyqtSignal(object)
    def __init__(self, parent=None):
        Qsci.QsciScintilla.__init__(self, parent)
        self.setLexer(Qsci.QsciLexerXML())
        self.setCaretLineVisible(True)
        self.setMarginLineNumbers(0, True)
        fontmetrics = QtGui.QFontMetrics(self.font())
        #self.setMarginsFont(font)
        self.setMarginWidth(0, fontmetrics.width("0000") + 2)
        #self.setMarginsBackgroundColor(QColor("#cccccc"))

    def focusOutEvent(self, event):
        self.editing_finished.emit(self)

class FeescaleEditor(QtGui.QMainWindow):
    _checking_files = False
    _known_deleted_parsers = []
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.window_title = _("Feescale Editor")
        self.setWindowTitle(self.window_title)
        self.loading = True

        self.list_view = QtGui.QListView()

        statusbar = QtGui.QStatusBar()
        self.setStatusBar(statusbar)

        #: a pointer to the label in the statusbar
        self.cursor_pos_label = QtGui.QLabel("Line 0, Column 0")
        statusbar.addPermanentWidget(self.cursor_pos_label)

        self.main_toolbar = QtGui.QToolBar()
        self.main_toolbar.setObjectName("Main Toolbar")
        self.main_toolbar.toggleViewAction().setText(_("Toolbar"))

        self.prefs_toolbar = QtGui.QToolBar()
        self.prefs_toolbar.setObjectName("Prefs Toolbar")
        self.prefs_toolbar.toggleViewAction().setText(_("Preferences Toolbar"))

        self.addToolBar(QtCore.Qt.TopToolBarArea, self.main_toolbar)
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.prefs_toolbar)

        menu_file = QtGui.QMenu(_("&File"), self)
        menu_edit = QtGui.QMenu(_("&Edit"), self)
        menu_database = QtGui.QMenu(_("&Database"), self)
        menu_tools = QtGui.QMenu(_("&Tools"), self)
        menu_preferences = QtGui.QMenu(_("&Preferences"), self)

        self.menuBar().addMenu(menu_file)
        self.menuBar().addMenu(menu_edit)
        self.menuBar().addMenu(menu_database)
        self.menuBar().addMenu(menu_tools)
        self.menuBar().addMenu(menu_preferences)

        icon = QtGui.QIcon(":database.png")
        action_pull = QtGui.QAction(icon, _("Pull"), self)
        action_pull.setToolTip(
        _("generate local files containing the database feescales"))

        icon = QtGui.QIcon(":database.png")
        action_commit = QtGui.QAction(icon, _("Commit"), self)
        action_commit.setToolTip(_("Commit changes to database"))

        icon = QtGui.QIcon.fromTheme("document-save")
        action_save = QtGui.QAction(icon, _("Save File"), self)
        action_save.setToolTip(_("Save Current File"))

        icon = QtGui.QIcon.fromTheme("document-save-as")
        action_save_as = QtGui.QAction(icon, _("Save File As"), self)
        action_save_as.setToolTip(_("Save Current File to a new location"))

        icon = QtGui.QIcon.fromTheme("document-save")
        action_save_all = QtGui.QAction(icon, _("Save All Files"), self)
        action_save_all.setToolTip(_("Save All Local Files"))

        icon = QtGui.QIcon.fromTheme("view-refresh")
        action_refresh = QtGui.QAction(icon, _("Refresh"), self)
        action_refresh.setToolTip(_("refresh local files"))

        action_increment = QtGui.QAction(_("Increase/decrease fees"), self)
        action_increment.setToolTip(_("Apply a percentage"))

        action_zero_charges = QtGui.QAction(
            _("Zero Patient Contributions"), self)
        action_zero_charges.setToolTip(
            _("Set all patient charges to Zero in the current feescale"))

        icon = QtGui.QIcon.fromTheme("application-exit")
        action_quit = QtGui.QAction(icon, _("Quit"), self)

        self.main_toolbar.addAction(action_pull)
        self.main_toolbar.addAction(action_commit)
        self.main_toolbar.addAction(action_save)
        self.main_toolbar.addAction(action_save_as)
        self.main_toolbar.addAction(action_save_all)
        self.main_toolbar.addAction(action_refresh)
        self.main_toolbar.addAction(action_quit)

        menu_file.addAction(action_save)
        menu_file.addAction(action_save_as)
        menu_file.addAction(action_save_all)
        menu_file.addAction(action_refresh)
        menu_file.addAction(action_quit)

        menu_database.addAction(action_pull)
        menu_database.addAction(action_commit)

        menu_tools.addAction(action_increment)
        menu_tools.addAction(action_zero_charges)

        self.tab_widget = QtGui.QTabWidget()

        self.feescale_parsers = OrderedDict()
        self.text_editors = []
        self.feescale_handler = feescale_handler
        self.load_feescales()

        self.action_refactor = QtGui.QAction(_("XML tidy"), self)
        self.action_refactor.triggered.connect(self.refactor)

        self.action_check_parseable = QtGui.QAction(_("Check Well Formed"), self)
        self.action_check_parseable.triggered.connect(self.check_parseable)

        self.action_check_validity = QtGui.QAction(_("Check Validity"), self)
        self.action_check_validity.triggered.connect(self.check_validity)

        menu_preferences.addAction(self.action_refactor)
        menu_preferences.addAction(self.action_check_parseable)
        menu_preferences.addAction(self.action_check_validity)

        self.prefs_toolbar.addAction(self.action_refactor)
        self.prefs_toolbar.addAction(self.action_check_parseable)
        self.prefs_toolbar.addAction(self.action_check_validity)

        splitter = QtGui.QSplitter()
        splitter.addWidget(self.list_view)
        splitter.addWidget(self.tab_widget)
        splitter.setSizes([150, 650])
        self.setCentralWidget(splitter)

        action_save.triggered.connect(self.save)
        action_save_as.triggered.connect(self.save_as)
        action_save_all.triggered.connect(self.save_files)
        action_refresh.triggered.connect(self.refresh_files)

        action_pull.triggered.connect(self.pull_xml)
        action_commit.triggered.connect(self.apply_changes)

        action_increment.triggered.connect(self.increase_fees)
        action_zero_charges.triggered.connect(self.zero_charges)

        action_quit.triggered.connect(
            QtGui.QApplication.instance().closeAllWindows)

        self.tab_widget.currentChanged.connect(self.view_feescale)
        QtCore.QTimer.singleShot(1000, self.view_feescale)


        QtGui.QApplication.instance().focusChanged.connect(
            self._focus_changed)

    def advise(self, message, importance=0):
        '''
        notify user
        '''
        if importance is 0:
            LOGGER.debug(message)
            m = QtGui.QMessageBox(self)
            m.setText(message)
            m.setIcon(m.information)
            m.setStandardButtons(QtGui.QMessageBox.NoButton)
            m.setWindowTitle(_("advisory"))
            m.setModal(False)
            QtCore.QTimer.singleShot(3*1000, m.accept)
            m.show()
        elif importance == 1:
            LOGGER.info(message)
            QtGui.QMessageBox.information(self, _("Advisory"), message)
        else:
            LOGGER.warning(message)
            QtGui.QMessageBox.warning(self, _("Error"), message)

    def sizeHint(self):
        return QtCore.QSize(800,500)

    def closeEvent(self, event=None):
        '''
        called when application closes.
        '''
        if self.is_dirty:
            message = u"<b>%s</b><hr />%s"%(
                _("WARNING - you have unsaved changes!"),
                _("Are you sure you want to quit?"))

            if QtGui.QMessageBox.question(self, _("Confirm"),
            message,
            QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel,
            QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Cancel:
                event.ignore()

    def _focus_changed(self, o1d_widget, new_widget):
        if o1d_widget is None:
            self._check_for_newer_local_files()

    def _check_for_newer_local_files(self):
        if self._checking_files:
            return
        self._checking_files = True
        for parser in self.feescale_parsers.values():
            if parser in self._known_deleted_parsers:
                pass
            elif parser.is_deleted:
                message = u"%s<br />%s<hr />%s"% (parser.filepath,
                _("has been deleted!"),
                _("Save now?") )
                if QtGui.QMessageBox.question(self, _("Question"),
                message,
                QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:
                    self.feescale_handler.save_xml(parser.ix, parser.text)
                    self.advise(_("File Saved"), 1)
                else:
                    self._known_deleted_parsers.append(parser)

            elif parser.is_externally_modified:
                message = u"%s<br />%s<hr />%s"% (parser.filepath,
                _("has been modified!"),
                _("Do you want to reload now and lose current changes?") \
                if parser.is_dirty else _("Do you want to reload now?"))

                if QtGui.QMessageBox.question(self, _("Question"),
                message,
                QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:
                    LOGGER.debug(
                    "reloading externally modified %s"% parser.filepath)
                    parser.refresh()
                    self.view_feescale(self.tab_widget.currentIndex())

                parser.reset_orig_modified()

        self._checking_files = False

    def load_feescales(self):
        self.loading = True
        self.text_editors = []
        self.feescale_parsers = OrderedDict()
        for ix, filepath in self.feescale_handler.local_files:
            try:
                fp = FeescaleParser(filepath)
                fp.ix = ix
            except:
                message = u"%s '%s'"% (_("unable to parse file"), filepath)
                self.advise(message, 2)
                LOGGER.exception(message)
                continue

            editor = XMLEditor()
            editor.textChanged.connect(self.text_changed)
            editor.editing_finished.connect(self.te_editing_finished)
            editor.cursorPositionChanged.connect(self.cursor_position_changed)

            title = "feescale %d"% ix
            self.feescale_parsers[title] = fp
            self.text_editors.append(editor)

            self.tab_widget.addTab(editor, title)

        self.loading = False

    def view_feescale(self, i=0):
        while self.loading:
            QtCore.QTimer.singleShot(1000, self.view_feescale)
            return
        if len(self.text_editors) > 1:
            text = self.current_parser.text
            self.text_editors[i].setText(text)
            self.setWindowTitle(
            "%s - %s" %(self.window_title, self.current_parser.description))
            self.update_index()
        else:
            if QtGui.QMessageBox.question(self, _("Information"),
            "%s %s<hr />%s"% (_("You have no local copies of the feescales"" "
            "stored in the database."),
            _("This is a requirement before editing can be performed."),
            _("Would you like to fetch and save these now?")),
            QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel,
            QtGui.QMessageBox.Ok) == QtGui.QMessageBox.Ok:
                self.get_files_from_database()

    def get_files_from_database(self):
        QtGui.QApplication.instance().setOverrideCursor(QtCore.Qt.WaitCursor)
        self.feescale_handler.get_local_xml_versions()
        QtGui.QApplication.instance().restoreOverrideCursor()
        self.load_feescales()

    def update_index(self):
        list_model = FeescaleListModel(self.current_parser)
        self.list_view.setModel(list_model)
        self.list_view.selectionModel().currentRowChanged.connect(
            self.list_view_row_changed)

    @property
    def text_edit(self):
        return self.text_editors[self.tab_widget.currentIndex()]

    @property
    def current_parser(self):
        return self.feescale_parsers.values()[self.tab_widget.currentIndex()]

    def refactor(self):
        if not self.check_parseable(show_message=False):
            return
        xml = unicode(self.text_edit.text().toUtf8())
        xml = re.sub(">[\s]*<", "><", xml)
        dom = minidom.parseString(xml)
        self.text_edit.setText(dom.toprettyxml())

    def check_parseable(self, action=None, show_message=True):
        xml = self.text_edit.text().toUtf8()
        try:
            minidom.parseString(xml)
            if show_message:
                self.advise(_("feescale is well formed"), 1)
            return True
        except Exception as exc:
            self.advise(u"<b>%s</b><hr />%s"% (
                _("feescale is not well formed"), exc.message), 2)
        return False

    def check_validity(self):
        xml = self.text_edit.text().toUtf8()
        result, message = self.current_parser.check_validity(xml)
        if result:
            self.advise(_("feescale is valid"), 1)
        else:
            self.advise(_(message), 1)

    def list_view_row_changed(self, new_index, old_index):
        self.find_item(new_index)

    def find_item(self, index):
        item_count = 0
        for lineno, line in enumerate(self.text_edit.text().split("\n")):
            if item_count == index.row()+1:
                self.text_edit.setFocus(True)
                self.text_edit.setCursorPosition(lineno-1, 0)
                self.text_edit.ensureCursorVisible()
                break

            if "<item"in line:
                item_count += 1

    def increase_fees(self):
        percentage, result = QtGui.QInputDialog.getDouble(
            self, _("Modify all fees"),
            _("Please enter a percentage"), 0, -100, 100, 2)
        if not result:
            return
        self.current_parser.increase_fees(percentage)
        self.text_edit.setText(self.current_parser.text)

    def zero_charges(self):
        if QtGui.QMessageBox.question(self, _("Confirm"),
        _("Zero all patient charges in the current feescale?"),
        QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel,
        QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Ok:
            self.current_parser.zero_charges()
            self.text_edit.setText(self.current_parser.text)

    def pull_xml(self):
        self._checking_files = True
        if QtGui.QMessageBox.question(self, _("confirm"),
        _("Would you like to find or update local copies of your feescales?"),
        QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel
        ) == QtGui.QMessageBox.Cancel:
            return
        in_use_only = QtGui.QMessageBox.question(self, _("question"),
        _("Include legacy feecales?"),
        QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
        QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes
        no_saved = 0
        for ix, xml_data in self.feescale_handler.get_feescales_from_database(
        in_use_only):
            filepath = self.feescale_handler.index_to_local_filepath(ix)
            if os.path.isfile(filepath):
                if QtGui.QMessageBox.question(self, _("question"),
                "%s '%s'"% (_("Overwrite file"), filepath),
                QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                QtGui.QMessageBox.No) == QtGui.QMessageBox.No:
                    continue
            self.feescale_handler.save_xml(ix, xml_data)
            no_saved += 1

        self.advise(u"%s %s"% (no_saved, _("Files saved")), 1)
        self._checking_files = False
        self._check_for_newer_local_files()

    def save_files(self):
        if QtGui.QMessageBox.question(self, _("confirm"),
        _("Save all files?"),
        QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel
        ) == QtGui.QMessageBox.Cancel:
            return

        i = 0
        for parser in self.feescale_parsers.itervalues():
            if parser in self._known_deleted_parsers:
                self._known_deleted_parsers.remove(parser)
            if not parser.is_dirty:
                continue

            if self.feescale_handler.save_xml(parser.ix, parser.text):
                parser.saved_xml = parser.text
                parser.reset_orig_modified()
                i += 1
        self.advise(u"%s %s"% (i, _("Files saved")), 1)

    def save(self):
        self.save_as(filepath = self.current_parser.filepath)

    def save_as(self, bool_=None, filepath=None):
        '''
        save the template, so it can be re-used in future
        '''
        LOGGER.debug(filepath)
        parser = self.current_parser
        try:
            if filepath is None:
                filepath = QtGui.QFileDialog.getSaveFileName(self,
                _("save as"),parser.filepath,
                "%s %s"% (_("xml_files"),"(*.xml)"))
            if filepath == '':
                return
            if not re.match(".*\.xml$", filepath):
                filepath += ".xml"
            f = open(filepath, "w")
            f.write(parser.text)
            f.close()
            if filepath != parser.filepath:
                self.advise("%s %s"% (_("Copy saved to"), filepath), 1)
                if os.path.dirname(filepath) == FEESCALE_DIR:
                    self.advise(_("Reload files to edit the new feescale"), 1)
            else:
                if parser in self._known_deleted_parsers:
                    self._known_deleted_parsers.remove(parser)
                self.advise(_("File Saved"), 1)
        except Exception as exc:
            LOGGER.exception("unable to save")
            self.advise(_("File not saved")+" - %s"% exc, 2)


    def refresh_files(self):
        if self.is_dirty and (
        QtGui.QMessageBox.question(self, _("confirm"),
        u"<b>%s</b><hr />%s"%(
        _("Warning - you have unsaved changes,"" "
        "if you refresh now, these will be lost"),
        _("Refresh anyway?")),
        QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel
        ) == QtGui.QMessageBox.Cancel):
            return

        for fp in self.feescale_parsers.values():
            fp.refresh()
        self.view_feescale(self.tab_widget.currentIndex())

    def apply_changes(self):
        if QtGui.QMessageBox.question(self, _("confirm"),
        _("commit all local files to database?"),
        QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel
        ) == QtGui.QMessageBox.Ok:
            message = self.feescale_handler.update_db_all()
            LOGGER.info("message")
            self.advise("<pre>%s</pre>"% message, 1)

    def cursor_position_changed(self, row, col):
        self.cursor_pos_label.setText("Line %d, Column %d"% (row+1, col))

    def text_changed(self):
        new_text = self.text_edit.text()
        if self.current_parser.text.count("\n") == new_text.count("\n"):
            return
        if self.current_parser.set_edited_text(new_text):
            self.update_index()

    def te_editing_finished(self, te):
        i = self.text_editors.index(te)
        new_text = te.text()
        self.feescale_parsers.values()[i].set_edited_text(new_text)

    @property
    def is_dirty(self):
        try:
            for parser in self.feescale_parsers.values():
                if parser.is_dirty:
                    LOGGER.debug("%s is dirty"% parser.filepath)
                    return True
            return False
        except:
            LOGGER.exception("property_exception")

if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    app = QtGui.QApplication(sys.argv)
    mw = FeescaleEditor()
    mw.show()
    app.exec_()
