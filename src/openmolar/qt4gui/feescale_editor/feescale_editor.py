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

from .feescale_parser import FeescaleParser
from .feescale_list_model import ItemsListModel, ComplexShortcutsListModel
from .feescale_xml_editor import XMLEditor
from .feescale_compare_items_dockwidget import CompareItemsDockWidget
from .feescale_input_dialogs import (PercentageInputDialog,
                                     RoundupFeesDialog,
                                     ChargePercentageInputDialog)
from .feescale_diff_dialog import DiffDialog
from .feescale_choice_dialog import ChoiceDialog
from .new_feescale_dialog import NewFeescaleDialog
from openmolar.dbtools.feescales import feescale_handler, FEESCALE_DIR

from collections import OrderedDict
from functools import partial
import logging
import re
import os
import sys
from gettext import gettext as _
from xml.dom import minidom

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

LOGGER = logging.getLogger("openmolar")


class ControlPanel(QtWidgets.QTabWidget):
    item_selected = QtCore.pyqtSignal(object)
    shortcut_selected = QtCore.pyqtSignal(object)
    compare_item_signal = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        QtWidgets.QTabWidget.__init__(self, parent)
        self.items_list_view = QtWidgets.QListView()
        self.complex_shortcuts_list_view = QtWidgets.QListView()

        self.addTab(self.items_list_view, "Items")
        self.addTab(self.complex_shortcuts_list_view, "Complex Shortcuts")

        self.items_list_view.doubleClicked.connect(self.show_item_context_menu)

    def set_parser(self, parser):
        list_model = ItemsListModel(parser)
        self.items_list_view.setModel(list_model)
        self.items_list_view.selectionModel().currentRowChanged.connect(
            self._item_selected)

        list_model = ComplexShortcutsListModel(parser)
        self.complex_shortcuts_list_view.setModel(list_model)
        self.complex_shortcuts_list_view.selectionModel(
        ).currentRowChanged.connect(self._shortcut_selected)

    def _item_selected(self, new_index, old_index):
        self.item_selected.emit(new_index)

    def _shortcut_selected(self, new_index, old_index):
        self.shortcut_selected.emit(new_index)

    def show_item_context_menu(self, index):
        id = self.items_list_view.model().id_from_index(index)
        qmenu = QtWidgets.QMenu(self)

        compare_action = QtWidgets.QAction(
            "%s %s %s" % (_("Compare"),
                          id,
                          _("with similar ids in other feescales")
                          ),
            self)
        cancel_action = QtWidgets.QAction(_("Cancel"), self)
        # not connected to anything.. f clicked menu will simply die!

        compare_action.triggered.connect(
            partial(self.compare_item_signal.emit, id))

        qmenu.addAction(compare_action)
        qmenu.addSeparator()
        qmenu.addAction(cancel_action)

        qmenu.setDefaultAction(compare_action)

        point = self.items_list_view.mapFromGlobal(QtGui.QCursor.pos())
        point = QtGui.QCursor.pos()
        qmenu.exec_(point)


class FeescaleEditor(QtWidgets.QMainWindow):
    _checking_files = False
    _known_deleted_parsers = []
    _compare_items_dockwidget = None
    search_text = ""
    closed_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.window_title = _("Feescale Editor")
        self.setWindowTitle(self.window_title)
        self.is_loading = True

        statusbar = QtWidgets.QStatusBar()
        self.setStatusBar(statusbar)

        self.control_panel = ControlPanel()
        self.control_panel.item_selected.connect(self.find_item)
        self.control_panel.compare_item_signal.connect(self.compare_item)
        self.control_panel.shortcut_selected.connect(self.find_shortcut)

        self.list_view = self.control_panel.items_list_view

        #: a pointer to the label in the statusbar
        self.cursor_pos_label = QtWidgets.QLabel("Line 0, Column 0")
        statusbar.addPermanentWidget(self.cursor_pos_label)

        self.main_toolbar = QtWidgets.QToolBar()
        self.main_toolbar.setObjectName("Main Toolbar")
        self.main_toolbar.toggleViewAction().setText(_("Toolbar"))

        self.prefs_toolbar = QtWidgets.QToolBar()
        self.prefs_toolbar.setObjectName("Prefs Toolbar")
        self.prefs_toolbar.toggleViewAction().setText(_("Preferences Toolbar"))

        self.diffs_toolbar = QtWidgets.QToolBar()
        self.diffs_toolbar.setObjectName("Diffs Toolbar")
        self.diffs_toolbar.toggleViewAction().setText(_("Diffs Toolbar"))

        self.addToolBar(QtCore.Qt.TopToolBarArea, self.main_toolbar)
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.prefs_toolbar)
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.diffs_toolbar)

        menu_file = QtWidgets.QMenu(_("&File"), self)
        menu_edit = QtWidgets.QMenu(_("&Edit"), self)
        menu_database = QtWidgets.QMenu(_("&Database"), self)
        menu_tools = QtWidgets.QMenu(_("&Tools"), self)
        menu_preferences = QtWidgets.QMenu(_("&Preferences"), self)
        menu_diffs = QtWidgets.QMenu(_("Diffs"), self)

        self.menuBar().addMenu(menu_file)
        self.menuBar().addMenu(menu_edit)
        self.menuBar().addMenu(menu_database)
        self.menuBar().addMenu(menu_tools)
        self.menuBar().addMenu(menu_diffs)
        self.menuBar().addMenu(menu_preferences)

        icon = QtGui.QIcon(":database.png")
        action_pull = QtWidgets.QAction(icon, _("Pull"), self)
        action_pull.setToolTip(
            _("generate local files containing the database feescales"))

        icon = QtGui.QIcon(":database.png")
        action_commit = QtWidgets.QAction(icon, _("Commit"), self)
        action_commit.setToolTip(_("Commit changes to database"))

        icon = QtGui.QIcon.fromTheme("document-new")
        action_new = QtWidgets.QAction(icon, _("New Feescale"), self)
        action_new.setToolTip(_("Create a Feescale"))

        icon = QtGui.QIcon.fromTheme("document-save")
        action_save = QtWidgets.QAction(icon, _("Save File"), self)
        action_save.setShortcut("Ctrl+S")
        action_save.setToolTip(_("Save Current File"))

        icon = QtGui.QIcon.fromTheme("document-save-as")
        action_save_as = QtWidgets.QAction(icon, _("Save File As"), self)
        action_save_as.setToolTip(_("Save Current File to a new location"))

        icon = QtGui.QIcon.fromTheme("document-save")
        action_save_all = QtWidgets.QAction(icon, _("Save All Files"), self)
        action_save_all.setToolTip(_("Save All Local Files"))

        icon = QtGui.QIcon.fromTheme("view-refresh")
        action_refresh = QtWidgets.QAction(icon, _("Refresh"), self)
        action_refresh.setToolTip(_("refresh local files"))

        icon = QtGui.QIcon.fromTheme("document-find")
        action_find = QtWidgets.QAction(icon, _("Find"), self)
        action_find.setShortcut("Ctrl+F")
        action_find.setToolTip(
            _("Search current file for first forward match of entered text"))

        action_find_again = QtWidgets.QAction(icon, _("Find Again"), self)
        action_find_again.setShortcut("Ctrl+G")
        action_find_again.setToolTip(_("Search current file again for text"))

        action_increment = QtWidgets.QAction(_("Increase/decrease fees"), self)
        action_increment.setToolTip(_("Apply a percentage"))

        action_roundup = QtWidgets.QAction(_("Round fees up/down"), self)
        action_roundup.setToolTip(
            _("Round fees up or down to a specified accuracy"))

        action_charges = QtWidgets.QAction(
            _("Relate charges to fees by percentage"), self)

        action_zero_charges = QtWidgets.QAction(
            _("Zero Patient Contributions"), self)
        action_zero_charges.setToolTip(
            _("Set all patient charges to Zero in the current feescale"))

        icon = QtGui.QIcon.fromTheme("application-exit")
        action_quit = QtWidgets.QAction(icon, _("Quit"), self)

        action_diff = QtWidgets.QAction(_("Show Database Diff"), self)
        action_diff.setToolTip(
            _("Show the diff between the current file and the "
              "corresponding file stored in the database"))

        action_compare = QtWidgets.QAction(_("Compare 2 Feescales"), self)
        action_compare.setToolTip(
            _("Show the diff between the current file and a selected other"))

        self.main_toolbar.addAction(action_new)
        self.main_toolbar.addAction(action_save)
        self.main_toolbar.addAction(action_save_as)
        self.main_toolbar.addAction(action_save_all)
        self.main_toolbar.addAction(action_refresh)
        self.main_toolbar.addAction(action_quit)
        self.main_toolbar.addSeparator()
        self.main_toolbar.addAction(action_pull)
        self.main_toolbar.addAction(action_commit)

        menu_file.addAction(action_new)
        menu_file.addSeparator()
        menu_file.addAction(action_save)
        menu_file.addAction(action_save_as)
        menu_file.addAction(action_save_all)
        menu_file.addSeparator()
        menu_file.addAction(action_refresh)
        menu_file.addSeparator()
        menu_file.addAction(action_quit)

        menu_edit.addAction(action_find)
        menu_edit.addAction(action_find_again)

        menu_database.addAction(action_pull)
        menu_database.addAction(action_commit)

        menu_tools.addAction(action_increment)
        menu_tools.addAction(action_roundup)
        menu_tools.addAction(action_charges)
        menu_tools.addAction(action_zero_charges)

        menu_diffs.addAction(action_diff)
        menu_diffs.addAction(action_compare)

        self.tab_widget = QtWidgets.QTabWidget()

        self.feescale_parsers = OrderedDict()
        self.text_editors = []
        self.feescale_handler = feescale_handler
        self.feescale_handler.check_dir()
        self.action_refactor = QtWidgets.QAction(_("XML tidy"), self)
        self.action_refactor.triggered.connect(self.refactor)

        self.action_check_parseable = QtWidgets.QAction(
            _("Check Well Formed"), self)
        self.action_check_parseable.triggered.connect(self.check_parseable)

        self.action_check_validity = QtWidgets.QAction(_("Check Validity"), self)
        self.action_check_validity.triggered.connect(self.check_validity)

        menu_preferences.addAction(self.action_refactor)
        menu_preferences.addAction(self.action_check_parseable)
        menu_preferences.addAction(self.action_check_validity)

        self.prefs_toolbar.addAction(self.action_refactor)
        self.prefs_toolbar.addAction(self.action_check_parseable)
        self.prefs_toolbar.addAction(self.action_check_validity)

        self.diffs_toolbar.addAction(action_diff)
        self.diffs_toolbar.addAction(action_compare)

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self.control_panel)
        splitter.addWidget(self.tab_widget)
        splitter.setSizes([150, 650])
        self.setCentralWidget(splitter)

        action_new.triggered.connect(self.new_feescale)
        action_save.triggered.connect(self.save)
        action_save_as.triggered.connect(self.save_as)
        action_save_all.triggered.connect(self.save_files)
        action_refresh.triggered.connect(self.refresh_files)

        action_find.triggered.connect(self.find_text)
        action_find_again.triggered.connect(self.find_again)

        action_pull.triggered.connect(self.get_files_from_database)
        action_commit.triggered.connect(self.apply_changes)

        action_increment.triggered.connect(self.increase_fees)
        action_roundup.triggered.connect(self.roundup_fees)
        action_charges.triggered.connect(self.relate_charges_to_gross_fees)
        action_zero_charges.triggered.connect(self.zero_charges)

        action_diff.triggered.connect(self.show_database_diff)
        action_compare.triggered.connect(self.compare_files)

        self.tab_widget.currentChanged.connect(self.view_feescale)

        QtCore.QTimer.singleShot(1000, self.start_)

        QtWidgets.QApplication.instance().focusChanged.connect(
            self._focus_changed)
        action_quit.triggered.connect(
            QtWidgets.QApplication.instance().closeAllWindows)

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
                    self,
                    _("Confirm"),
                    message,
                    QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
                    QtWidgets.QMessageBox.Cancel) == QtWidgets.QMessageBox.Cancel:
                event.ignore()
                return
        self.closed_signal.emit()

    def _focus_changed(self, o1d_widget, new_widget):
        if o1d_widget is None:
            self._check_for_newer_local_files()

    def _check_for_newer_local_files(self):
        if self._checking_files:
            return
        self._checking_files = True
        for parser in list(self.feescale_parsers.values()):
            if parser in self._known_deleted_parsers:
                pass
            elif parser.is_deleted:
                message = "%s<br />%s<hr />%s" % (
                    parser.filepath,
                    _("has been deleted!"),
                    _("Save now?"))
                if QtWidgets.QMessageBox.question(
                        self,
                        _("Question"),
                        message,
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                        QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes:
                    self.feescale_handler.save_xml(parser.ix, parser.text)
                    self.advise(_("File Saved"), 1)
                else:
                    self._known_deleted_parsers.append(parser)

            elif parser.is_externally_modified:
                message = "%s<br />%s<hr />%s" % (
                    parser.filepath,
                    _("has been modified!"),
                    _("Do you want to reload now and lose current changes?")
                    if parser.is_dirty else _("Do you want to reload now?"))

                if QtWidgets.QMessageBox.question(
                        self,
                        _("Question"),
                        message,
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                        QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes:
                    LOGGER.debug("reloading externally modified %s",
                                 parser.filepath)
                    parser.refresh()
                    self.view_feescale(self.tab_widget.currentIndex())

                parser.reset_orig_modified()

        self._checking_files = False

    def start_(self):
        self.get_files_from_database()
        self.load_feescales()
        self.view_feescale(0)

    def load_feescales(self):
        self.is_loading = True

        # if reloading.. disconnect signals.
        for editor in self.text_editors:
            editor.editing_finished.disconnect(self.te_editing_finished)
            editor.cursorPositionChanged.disconnect(
                self.cursor_position_changed)
            editor.deleteLater()

        self.text_editors = []
        self.feescale_parsers = OrderedDict()
        for ix, filepath in self.feescale_handler.local_files:
            self.load_feescale_from_filepath(ix, filepath)
        self.is_loading = False
        self.advise("%d local files created/loaded for editing" %
                    self.feescale_handler.count, 1)

    def load_feescale_from_filepath(self, ix, filepath):
        fp = FeescaleParser(filepath, ix)
        try:
            fp.parse_file()
        except:
            message = "%s '%s'" % (_("unable to parse file"), filepath)
            self.advise(message, 2)
            LOGGER.exception(message)

        editor = XMLEditor()
        editor.editor_settings()
        editor.textChanged.connect(self.text_changed)
        editor.editing_finished.connect(self.te_editing_finished)
        editor.cursorPositionChanged.connect(self.cursor_position_changed)

        title = fp.label_text
        self.feescale_parsers[title] = fp
        self.text_editors.append(editor)

        self.tab_widget.addTab(editor, title)
        tooltip = "%s\n%s" % (fp.tablename, fp.description)
        LOGGER.debug("setting tab tool tip %s", tooltip.replace("\n", " "))
        self.tab_widget.setTabToolTip(ix, tooltip)

    def view_feescale(self, i=0):
        while self.is_loading:
            QtCore.QTimer.singleShot(1000, self.view_feescale)
            return
        if len(self.text_editors) > 1:
            text = self.current_parser.text
            self.text_editors[i].setText(text)
            self.setWindowTitle(
                "%s - %s" % (self.window_title,
                             self.current_parser.description))
            self.update_index()
        else:
            QtWidgets.QMessageBox.information(
                self,
                _("Information"),
                _("You appear to have no feescales installed in your database")
            )

    def get_files_from_database(self):
        '''
        gets files from the database at startup
        '''
        unwritten, modified = \
            self.feescale_handler.non_existant_and_modified_local_files()

        for xml_file in unwritten:
            f = open(xml_file.filepath, "w")
            f.write(xml_file.data)
            f.close()

        self._checking_files = True

        for xml_file in modified:
            message = "%s '%s' %s<hr />%s" % (
                _("Local Feescale"), xml_file.filepath,
                _("differs from the database version"),
                _("Do you wish to overwrite it with the stored data?"))

            mb = QtWidgets.QMessageBox(None)
            mb.setWindowTitle(_("Confirm"))
            mb.setText(message)
            mb.setIcon(mb.Question)
            mb.addButton(_("Show Diff"), mb.DestructiveRole)
            but = mb.addButton(mb.Cancel)
            but.setText(_("Keep Local File Unchanged"))
            but = mb.addButton(mb.Ok)
            but.setText(_("Overwrite Local File"))

            result = mb.exec_()
            if result not in (mb.Ok, mb.Cancel):
                # show diff
                f = open(xml_file.filepath, "r")
                local_data = f.read()
                f.close()
                dl = DiffDialog(xml_file.data, local_data)
                dl.apply_but.setText(_("Overwrite Local File"))
                dl.cancel_but.setText(_("Keep Local File Unchanged"))
                dl.enableApply()
                result = mb.Ok if dl.exec_() else mb.Cancel

            if result == mb.Ok:
                LOGGER.debug("saving file")
                f = open(xml_file.filepath, "w")
                f.write(xml_file.data)
                f.close()
            else:
                LOGGER.debug("not saving file")

        self._checking_files = False
        self._check_for_newer_local_files()

    def update_index(self):
        self.control_panel.set_parser(self.current_parser)

    @property
    def text_edit(self):
        return self.text_editors[self.tab_widget.currentIndex()]

    @property
    def current_parser(self):
        i = self.tab_widget.currentIndex()
        return list(self.feescale_parsers.values())[i]

    def refactor(self):
        if not self.check_parseable(show_message=False):
            return
        xml = str(self.text_edit.text())
        xml = re.sub(">[\s]*<", "><", xml)
        dom = minidom.parseString(xml)

        # don't use setText here that updates orig_text and is_dirty won't work
        self.text_edit.update_text(dom.toprettyxml())

    def check_parseable(self, action=None, show_message=True):
        xml = self.text_edit.text()
        try:
            minidom.parseString(xml)
            if show_message:
                self.advise(_("feescale is well formed"), 1)
            return True
        except Exception as exc:
            self.advise("<b>%s</b><hr />%s" % (
                _("feescale is not well formed"), exc.message), 2)
        return False

    def check_validity(self):
        xml = self.text_edit.text()
        result, message = self.current_parser.check_validity(xml)
        if result:
            self.advise(_("feescale is valid"), 1)
        else:
            self.advise(message, 1)

    def find_item(self, index):
        item_count = 0
        for lineno, line in enumerate(self.text_edit.text().split("\n")):
            if item_count == index.row() + 1:
                self.text_edit.setFocus(True)
                self.text_edit.setFirstVisibleLine(lineno - 2)
                self.text_edit.setCursorPosition(lineno - 1, 0)
                self.text_edit.ensureCursorVisible()
                break

            if "<item"in line:
                item_count += 1
        if self._compare_items_dockwidget:
            id = self.list_view.model().id_from_index(index)
            self.compare_item(id)

    def compare_item(self, item_id):
        LOGGER.debug(item_id)
        self.compare_items_dockwidget.set_item_id(item_id)
        self.compare_items_dockwidget.show()

    @property
    def compare_items_dockwidget(self):
        if self._compare_items_dockwidget is None:
            self._compare_items_dockwidget = CompareItemsDockWidget(
                list(self.feescale_parsers.values()), self)
            self.addDockWidget(QtCore.Qt.BottomDockWidgetArea,
                               self._compare_items_dockwidget)
        return self._compare_items_dockwidget

    def find_shortcut(self, index):
        count_ = 0
        for lineno, line in enumerate(self.text_edit.text().split("\n")):
            if count_ == index.row() + 1:
                self.text_edit.setFocus(True)
                self.text_edit.setCursorPosition(lineno - 1, 0)
                self.text_edit.ensureCursorVisible()
                break

            if "<complex_shortcut"in line:
                count_ += 1

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

    def roundup_fees(self):
        dl = RoundupFeesDialog(self)
        if dl.exec_():
            if dl.alter_gross:
                func_ = self.current_parser.roundup_fees
            else:
                func_ = self.current_parser.roundup_charges
            func_(dl.round_value, dl.round_up, dl.round_down)

            self.text_edit.setText(self.current_parser.text)
            self.advise(dl.message, 1)

    def increase_fees(self):
        dl = PercentageInputDialog(self)
        if dl.exec_():
            if dl.alter_gross:
                self.current_parser.increase_fees(dl.percentage)
            else:
                self.current_parser.increase_charges(dl.percentage)
            self.text_edit.setText(self.current_parser.text)
            self.advise(dl.message, 1)

    def relate_charges_to_gross_fees(self):
        dl = ChargePercentageInputDialog(self)
        if dl.exec_():
            self.current_parser.relate_charges_to_gross_fees(
                dl.percentage, dl.leave_zero_charges_unchanged)
            self.text_edit.setText(self.current_parser.text)
            self.advise(dl.message, 1)

    def zero_charges(self):
        if QtWidgets.QMessageBox.question(
                self,
                _("Confirm"),
                _("Zero all patient charges in the current feescale?"),
                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
                QtWidgets.QMessageBox.Cancel) == QtWidgets.QMessageBox.Ok:
            self.current_parser.zero_charges()
            self.text_edit.setText(self.current_parser.text)

    def save_files(self):
        if QtWidgets.QMessageBox.question(
                self,
                _("confirm"),
                _("Save all files?"),
                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel) == \
                QtWidgets.QMessageBox.Cancel:
            return

        i = 0
        for parser in self.feescale_parsers.values():
            if parser in self._known_deleted_parsers:
                self._known_deleted_parsers.remove(parser)
            if not parser.is_dirty:
                continue

            if self.feescale_handler.save_xml(parser.ix, parser.text):
                parser.saved_xml = parser.text
                parser.reset_orig_modified()
                i += 1
        self.advise("%s %s" % (i, _("Files saved")), 1)

    def save(self):
        LOGGER.debug("save")
        self.save_as(filepath=self.current_parser.filepath)

    def new_feescale(self):
        LOGGER.debug("new_feescale")
        dl = NewFeescaleDialog(self)
        if dl.exec_():
            self.load_feescale_from_filepath(dl.ix, dl.filepath)
            self.tab_widget.setCurrentIndex(self.tab_widget.count()-1)

    def save_as(self, bool_=None, filepath=None):
        '''
        save the template, so it can be re-used in future
        '''
        LOGGER.debug(filepath)
        parser = self.current_parser
        try:
            if filepath is None:
                filepath = str(
                    QtWidgets.QFileDialog.getSaveFileName(
                        self,
                        _("save as"),
                        parser.filepath,
                        "%s (*.xml)" % _("xml_files"))
                )
            if filepath == '':
                return
            if not re.match(".*\.xml$", filepath):
                filepath += ".xml"
            f = open(filepath, "w")
            f.write(parser.text)
            f.close()
            if filepath != parser.filepath:
                self.advise("%s %s" % (_("Copy saved to"), filepath), 1)
                if os.path.dirname(filepath) == FEESCALE_DIR():
                    self.advise(_("Reload files to edit the new feescale"), 1)
            else:
                if parser in self._known_deleted_parsers:
                    self._known_deleted_parsers.remove(parser)
                parser.saved_xml = parser.text
                parser.reset_orig_modified()
                self.advise(_("File Saved"), 1)
        except Exception as exc:
            LOGGER.exception("unable to save")
            self.advise(_("File not saved") + " - %s" % exc, 2)

    def refresh_files(self):
        if self.is_dirty and (
                QtWidgets.QMessageBox.question(
                    self,
                    _("confirm"),
                    "<b>%s</b><hr />%s" % (
                        _("Warning - you have unsaved changes, "
                          "if you refresh now, these will be lost"),
                        _("Refresh anyway?")),
                    QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel) ==
                QtWidgets.QMessageBox.Cancel):
            return

        self.tab_widget.clear()
        self.load_feescales()

    def apply_changes(self):
        if self.is_dirty:
            self.advise(
                _("Please save local files before pushing to database"), 1)
            return
        if QtWidgets.QMessageBox.question(
                self,
                _("confirm"),
                _("update all existing feescales with data from "
                  "the local files?"),
                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel) == \
                QtWidgets.QMessageBox.Cancel:
            return

        message, insert_ids = self.feescale_handler.update_db_all()
        LOGGER.info("message")
        self.advise("<pre>%s</pre>" % message, 1)

        mappings = {}
        for ins_id in insert_ids:
            if QtWidgets.QMessageBox.question(
                    self,
                    _("confirm"),
                    "%s %s?" % (
                        _("Insert new Feescale"),
                        self.feescale_handler.index_to_local_filepath(ins_id)),
                    QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel) == \
                    QtWidgets.QMessageBox.Ok:
                mappings[ins_id] = self.feescale_handler.insert_db(ins_id)

        move_required = False
        for file_ix, db_ix in mappings.items():
            if file_ix != db_ix:
                move_required = True
                self.advise(
                    _("your local files will now be moved to "
                      "comply with the database indexes they have been given"),
                    1)
                break
        if not move_required:
            return

        # self._checking_files = True
        for file_ix in list(mappings.keys()):
            self.feescale_handler.temp_move(file_ix)
        for file_ix, db_ix in mappings.items():
            self.feescale_handler.final_move(file_ix, db_ix)
        self.refresh_files()

    def cursor_position_changed(self, row, col):
        self.cursor_pos_label.setText("Line %d, Column %d" % (row + 1, col))

    def text_changed(self):
        new_text = self.text_edit.text()
        # if self.current_parser.text.count("\n") == new_text.count("\n"):
        #    return
        if self.current_parser.set_edited_text(new_text):
            self.update_index()

    def te_editing_finished(self, te):
        i = self.text_editors.index(te)
        new_text = te.text()
        list(self.feescale_parsers.values())[i].set_edited_text(new_text)

    def show_database_diff(self):
        orig = self.feescale_handler.get_feescale_from_database(
            self.current_parser.ix)
        new = str(self.text_edit.text())
        dl = DiffDialog(orig, new)
        dl.exec_()

    def compare_files(self):
        options = []
        for i in range(self.tab_widget.count()):
            if i != self.tab_widget.currentIndex():
                options.append(self.tab_widget.tabText(i))

        if len(options) == 1:
            QtWidgets.QMessageBox.information(
                self,
                _("whoops"),
                _("you have no other files available for comparison"))
            return

        message = "%s<br /><b>%s (%s)</b><hr />%s" % (
            _("Which feescale would you like to compare "
              "with the current feescale"),
            self.current_parser.ix,
            self.current_parser.description,
            _("Please make a choice"))

        dl = ChoiceDialog(message, options, self)
        if dl.exec_():
            chosen = dl.chosen_index

            orig = str(self.text_edit.text())
            new = str(self.text_editors[chosen].text())
            dl = DiffDialog(orig, new)
            dl.exec_()

    @property
    def is_dirty(self):
        try:
            for parser in list(self.feescale_parsers.values()):
                if parser.is_dirty:
                    LOGGER.debug("%s is dirty" % parser.filepath)
                    return True
            return False
        except:
            LOGGER.exception("property_exception")


if __name__ == "__main__":
    from openmolar.qt4gui import resources_rc
    LOGGER.setLevel(logging.DEBUG)
    app = QtWidgets.QApplication(sys.argv)
    mw = FeescaleEditor()
    mw.show()
    app.exec_()
