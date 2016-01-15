#! /usr/bin/python
# -*- coding: utf-8 -*-

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2015 Neil Wallace <neil@openmolar.com>               # #
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

'''
schedule_control.py provides the DiaryScheduleController class for openmolar.
'''

from gettext import gettext as _
import logging

from PyQt4 import QtGui, QtCore, QtWebKit

from openmolar.settings import localsettings
from openmolar.dbtools.brief_patient import BriefPatient
from openmolar.dbtools import appointments

from openmolar.qt4gui.appointment_gui_modules.draggable_list \
    import DraggableList
from openmolar.qt4gui.appointment_gui_modules.list_models \
    import SimpleListModel, BlockListModel, ColouredItemDelegate

from openmolar.qt4gui.dialogs.find_patient_dialog import FindPatientDialog
from openmolar.qt4gui.dialogs.appt_settings_dialog import \
    ApptSettingsDialog, ApptSettingsResetDialog

from openmolar.qt4gui.pt_diary_widget import PtDiaryWidget

LOGGER = logging.getLogger("openmolar")

MAX_WAIT = 10  # maximum time pt waiting in between "joint" appointments

FEEDBACK = '''<html>
<head>
<link rel="stylesheet" href="%s" type="text/css">
</head>
<body class="highlighted-app">
<div class="center">
<h3>%%s</h3>
(%%s)<br />
<b>%%s<br />%%s - %%s</b>
</div>
<ol><li class="trt">%%s</li></ol>''' % localsettings.stylesheet


class DiaryScheduleController(QtGui.QStackedWidget):

    '''
    This widget lives down the left side of the diary widget.
    It provides a way of switching modes for the diary.
    '''

    BROWSE_MODE = 0
    SCHEDULE_MODE = 1
    BLOCK_MODE = 2
    NOTES_MODE = 3

    NOT_SEARCHING = 0
    SEARCHING_FORWARDS = 1
    SEARCHING_BACKWARDS = 2

    mode = BROWSE_MODE
    search_mode = NOT_SEARCHING

    appointment_selected = QtCore.pyqtSignal(object)
    patient_selected = QtCore.pyqtSignal(object)
    show_first_appointment = QtCore.pyqtSignal()
    chosen_slot_changed = QtCore.pyqtSignal()
    find_appt = QtCore.pyqtSignal(object)
    start_scheduling = QtCore.pyqtSignal()  # from embedded pt diary widget
    advice_signal = QtCore.pyqtSignal(object, object)

    pt = None
    primary_slots = []
    secondary_slots = []

    _chosen_slot = None

    finding_joint_appointments = False

    def __init__(self, parent=None):
        QtGui.QStackedWidget.__init__(self, parent)
        self.diary_widget = parent
        self.patient_label = QtGui.QLabel()

        icon = QtGui.QIcon(":/search.png")
        self.get_patient_button = QtGui.QPushButton(icon, "")
        self.get_patient_button.setMaximumWidth(40)

        self.appt_listView = DraggableList(self)
        self.block_listView = DraggableList(self)
        self.item_delegate = ColouredItemDelegate(self)

        self.appointment_model = SimpleListModel(self)
        self.appt_listView.setModel(self.appointment_model)
        self.appt_listView.setItemDelegate(self.item_delegate)
        self.appt_listView.setSelectionModel(
            self.appointment_model.selection_model)
        self.appt_listView.setSelectionMode(
            QtGui.QListView.ContiguousSelection)

        block_model = BlockListModel(self)
        self.block_listView.setModel(block_model)

        icon = QtGui.QIcon(":vcalendar.png")
        diary_button = QtGui.QPushButton(icon, _("Diary"))
        diary_button.setToolTip(_("Open the patient's diary"))

        icon = QtGui.QIcon(":settings.png")
        settings_button = QtGui.QPushButton(icon, _("Options"))
        settings_button.setToolTip(_("Appointment Settings"))

        icon = QtGui.QIcon(":back.png")
        self.prev_appt_button = QtGui.QPushButton(icon, "")
        self.prev_appt_button.setToolTip(_("Previous appointment"))

        icon = QtGui.QIcon(":forward.png")
        self.next_appt_button = QtGui.QPushButton(icon, "")
        self.next_appt_button.setToolTip(_("Next available appointment"))

        icon = QtGui.QIcon(":forward.png")
        self.next_day_button = QtGui.QPushButton(icon, "")
        self.next_day_button.setToolTip(_("Next Day or Week"))

        icon = QtGui.QIcon(":back.png")
        self.prev_day_button = QtGui.QPushButton(icon, "")
        self.prev_day_button.setToolTip(_("Previous Day or Week"))

        icon = QtGui.QIcon(":first.png")
        self.first_appt_button = QtGui.QPushButton(icon, "")
        self.first_appt_button.setToolTip(_("First available appointment"))

        self.appt_controls_frame = QtGui.QWidget()
        layout = QtGui.QGridLayout(self.appt_controls_frame)
        layout.setMargin(1)
        layout.setSpacing(2)
        layout.addWidget(diary_button, 0, 0, 1, 2)
        layout.addWidget(settings_button, 0, 3, 1, 2)
        layout.addWidget(self.prev_day_button, 1, 0)
        layout.addWidget(self.prev_appt_button, 1, 1)
        layout.addWidget(self.first_appt_button, 1, 2)
        layout.addWidget(self.next_appt_button, 1, 3)
        layout.addWidget(self.next_day_button, 1, 4)

        self.appt_controls_frame.setSizePolicy(
            QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,
                              QtGui.QSizePolicy.Minimum))

        self.search_criteria_webview = QtWebKit.QWebView(self)
        self.search_criteria_webview.setMinimumHeight(100)
        self.search_criteria_webview.setHtml(
            _("No appointment selected for scheduling"))

        # now arrange the stacked widget

        # page 0 - Browsing mode
        self.browsing_webview = QtWebKit.QWebView()
        self.reset_browsing_webview()
        self.addWidget(self.browsing_webview)

        # page 1 -- scheduling mode
        widg = QtGui.QWidget()
        layout = QtGui.QGridLayout(widg)
        layout.setMargin(0)
        layout.addWidget(self.patient_label, 0, 0)
        layout.addWidget(self.get_patient_button, 0, 1)
        layout.addWidget(self.appt_listView, 2, 0, 1, 2)
        layout.addWidget(self.appt_controls_frame, 3, 0, 1, 2)
        layout.addWidget(self.search_criteria_webview, 4, 0, 1, 2)
        self.addWidget(widg)

        # page 2 -- blocking mode
        widg = QtGui.QWidget()
        layout = QtGui.QVBoxLayout(widg)
        layout.addWidget(self.block_listView)
        self.addWidget(widg)

        # page 4 -- notes mode
        self.addWidget(QtGui.QLabel("Notes"))

        # connect signals
        self.get_patient_button.clicked.connect(self.find_patient)
        settings_button.clicked.connect(self.show_settings_dialog)
        self.prev_appt_button.clicked.connect(self.show_prev_appt)
        self.next_appt_button.clicked.connect(self.show_next_appt)
        self.prev_day_button.clicked.connect(self.show_prev_day)
        self.next_day_button.clicked.connect(self.show_next_day)
        self.first_appt_button.clicked.connect(self.find_first_appointment)

        diary_button.clicked.connect(self.show_pt_diary)

        self.appt_listView.selectionModel().selectionChanged.connect(
            self.selection_changed)
        self.appt_listView.doubleClicked.connect(self.appointment_2x_clicked)

    def set_mode(self, mode):
        if self.mode == mode:
            return

        if mode == self.SCHEDULE_MODE:
            self.update_patient_label()
            self.enable_scheduling_buttons()
        else:
            self.clear_slots()
        if mode == self.BROWSE_MODE:
            self.reset_browsing_webview()

        self.mode = mode
        self.setCurrentIndex(mode)

    def set_search_mode(self, mode):
        assert mode in (self.NOT_SEARCHING,
                        self.SEARCHING_FORWARDS, self.SEARCHING_BACKWARDS)
        self.search_mode = mode

    def cancel_search_mode(self):
        self.set_search_mode(self.NOT_SEARCHING)

    def set_search_future(self):
        self.set_search_mode(self.SEARCHING_FORWARDS)

    def set_search_past(self):
        self.set_search_mode(self.SEARCHING_BACKWARDS)

    @property
    def searching_future(self):
        return self.search_mode == self.SEARCHING_FORWARDS

    @property
    def searching_past(self):
        return self.search_mode == self.SEARCHING_BACKWARDS

    def set_patient(self, pt):
        self.clear()
        self.pt = pt
        if pt is not None:
            self.appointment_model.load_from_database(self.pt)
            self.patient_selected.emit(self.pt)
        self.enable_scheduling_buttons()

    def get_data(self):
        '''
        loads the appointment model from database, or clears if patient is None
        '''
        LOGGER.debug("schedule control get-data")
        if self.pt is None:
            self.clear()
            return
        self.appointment_model.load_from_database(self.pt)

    @property
    def patient_text(self):
        if self.pt:
            return "%s %s (%s)" % (
                self.pt.fname, self.pt.sname, self.pt.serialno)
        else:
            return _("No patient Selected")

    def find_patient(self):
        '''
        search and load a patient.
        '''
        dl = FindPatientDialog(self)
        if dl.exec_():
            self.clear()
            pt = BriefPatient(dl.chosen_sno)
            self.set_patient(pt)
            self.diary_widget.set_date(QtCore.QDate.currentDate())
        self.update_patient_label()

    def update_patient_label(self):
        self.patient_label.setText(self.patient_text)

    @property
    def selected_appointment(self):
        '''
        the appointment currently selected by user
        '''
        return self.appointment_model.currentAppt

    @property
    def secondary_appointment(self):
        '''
        the appointment jointly selected by user
        '''
        return self.appointment_model.secondaryAppt

    @property
    def app1_length(self):
        try:
            return self.appointment_model.currentAppt.length
        except AttributeError:
            return 0

    @property
    def app1_is_scheduled(self):
        try:
            return not self.appointment_model.currentAppt.unscheduled
        except AttributeError:
            LOGGER.debug("app1_is_scheduled")
            return False

    @property
    def app2_length(self):
        try:
            return self.appointment_model.secondaryAppt.length
        except AttributeError:
            return 0

    @property
    def app2_is_scheduled(self):
        try:
            return not self.appointment_model.secondaryAppt.unscheduled
        except AttributeError:
            LOGGER.debug("app2_is_scheduled")
            return False

    @property
    def ignore_emergency_spaces(self):
        return ApptSettingsDialog.ignore_emergency_spaces

    def set_selection_mode(self, mode):
        assert mode in (
            self.CLINICIAN_ANY,
            self.CLINICIAN_ANY_DENT,
            self.CLINICIAN_ANY_HYG,
            self.CLINICIAN_SELECTED), "selection mode misunderstood"
        self.dent_selection_mode = mode

    @property
    def selectedClinicians(self):
        return self.appointment_model.selectedClinicians

    def _appt_clinicians(self, appt):
        '''
        use the selected appointment and the chosen settings to see
        who could perform this treatment.
        '''
        if appt.dent in localsettings.activedent_ixs:
            if ApptSettingsDialog.dentist_policy == \
                    ApptSettingsDialog.CLINICIAN_ANY_DENT:
                return localsettings.activedent_ixs
            if ApptSettingsDialog.dentist_policy == \
                    ApptSettingsDialog.CLINICIAN_ANY:
                return \
                    localsettings.activedent_ixs + localsettings.activehyg_ixs
        elif appt.dent in localsettings.activehyg_ixs:
            if ApptSettingsDialog.hygienist_policy == \
                    ApptSettingsDialog.CLINICIAN_ANY_HYG:
                return localsettings.activehyg_ixs

        return (appt.dent, )

    @property
    def appt1_clinicians(self):
        '''
        what clinicians could provide the treatment in appointment 1?
        '''
        appt = self.appointment_model.currentAppt
        if appt:
            return self._appt_clinicians(appt)
        return ()

    @property
    def appt2_clinicians(self):
        '''
        what clinicians could provide the treatment in appointment 2?
        '''
        appt = self.appointment_model.secondaryAppt
        if appt:
            return self._appt_clinicians(appt)
        return ()

    @property
    def involvedClinicians(self):
        return self.appointment_model.involvedClinicians

    def sizeHint(self):
        return QtCore.QSize(180, 400)

    def update_appt_selection(self, appts):
        '''
        sync with the "patient diary" via signal/slot
        '''
        LOGGER.debug(
            "updating schedule controller appointments, appts='%s'", appts)
        if self.pt is None:
            return
        for appt in appts:
            if appt.serialno != self.pt.serialno:
                return
        self.appointment_model.set_selected_appointments(appts)

    def update_selected_appointment(self, appt):
        self.primary_slots = []
        self._chosen_slot = None
        self.enable_scheduling_buttons()

    def selection_changed(self, selection):
        LOGGER.debug("ScheduleControl.selection_changed")
        self.update_search_criteria_webview()
        self.enable_scheduling_buttons()
        try:
            app = self.appointment_model.data(selection.indexes()[-1],
                                              QtCore.Qt.UserRole)
        except IndexError:
            app = self.appointment_model.currentAppt
        self.appointment_selected.emit(app)

    def appointment_2x_clicked(self, index):
        LOGGER.debug("ScheduleControl.appointment_clicked")
        self.show_first_appointment.emit()

    def clear(self):
        self.appointment_model.clear()
        self.reset()

    def reset(self):
        self.reset_browsing_webview()
        self.primary_slots = []
        self.secondary_slots = []
        self._chosen_slot = None
        self.cancel_search_mode()
        self.finding_joint_appointments = False

    def show_settings_dialog(self):
        '''
        show the settings dialog
        '''
        LOGGER.info("showing the settings dialog")
        dl = ApptSettingsDialog(self)
        if dl.exec_():
            self.selection_changed(
                self.appt_listView.selectionModel().selection())

    @property
    def _chosen_slot_no(self):
        try:
            return self.primary_slots.index(self._chosen_slot)
        except ValueError:
            return 0

    def show_next_appt(self):
        self.set_search_future()
        try:
            self._chosen_slot = self.primary_slots[self._chosen_slot_no + 1]
            self.chosen_slot_changed.emit()
        except IndexError:
            self.show_next_day()

    def show_prev_appt(self):
        self.set_search_past()
        try:
            i = self._chosen_slot_no - 1
            if i < 0:
                raise IndexError
            self._chosen_slot = self.primary_slots[i]
            self.chosen_slot_changed.emit()
        except IndexError:
            self.show_prev_day()

    def show_next_day(self):
        '''
        catches the signal to make a big jump forwards.
        will jump a week if in week view
        '''
        self._chosen_slot = None
        self.set_search_future()
        self.diary_widget.step_date(True)

    def show_prev_day(self):
        '''
        catches the signal to make a big jump backwords.
        will jump a week if in week view
        '''
        self._chosen_slot = None
        self.set_search_past()
        self.diary_widget.step_date(False)

    @property
    def all_slots(self):
        for slot in self.primary_slots:
            yield slot
        for slot in self.secondary_slots:
            yield slot

    def clear_slots(self):
        # self.reset_browsing_webview()
        self._chosen_slot = None
        self.primary_slots = []
        self.secondary_slots = []

    def reset_browsing_webview(self):
        self.browsing_webview.setHtml("")

    def set_primary_slots(self, slots):
        self.primary_slots = []
        for slot in sorted(slots):
            if (slot.dent in self.appt1_clinicians and
                    slot.day_no not in self.excluded_days):
                self.primary_slots.append(slot)

    def set_secondary_slots(self, slots):
        LOGGER.debug("filtering secondary slots %s", slots)
        self.secondary_slots = []
        for slot in sorted(slots):
            slot.is_primary = False
            if (slot.dent in self.appt2_clinicians and
                    slot.day_no not in self.excluded_days):
                self.secondary_slots.append(slot)

    def set_slots_from_day_app_data(self, app_data):
        self.set_primary_slots([] if self.app1_is_scheduled else
                               app_data.slots(self.app1_length,
                                              self.ignore_emergency_spaces))
        app2_slots = []
        if self.is_searching_for_double_appointments and \
                not self.app2_is_scheduled:
            self.set_secondary_slots(
                app_data.slots(self.app2_length,
                               self.ignore_emergency_spaces,
                               busy_serialno=self.pt.serialno)
            )
            app1_slots = set([])
            if self.app1_is_scheduled:
                iterset = [self.appointment_model.currentAppt.to_freeslot()]
            else:
                iterset = self.primary_slots
            for app1_slot in iterset:
                for app2_slot in self.secondary_slots:
                    wait = app1_slot.wait_time(self.app1_length,
                                               self.app2_length,
                                               app2_slot)
                    if wait is not None and wait <= MAX_WAIT:
                        app2_slots.append(app2_slot)
                        app1_slots.add(app1_slot)
            if not self.app1_is_scheduled:
                self.set_primary_slots(app1_slots)

        self.set_secondary_slots(app2_slots)

    def get_weekview_slots(self, weekdates):
        '''
        calculate available slots for weekdates (list of QDates)
        '''
        today = QtCore.QDate.currentDate()
        startday = today if today in weekdates else weekdates[0]  # monday
        sunday = weekdates[6]  # sunday

        # check for suitable apts in the selected WEEK!
        all_slots = appointments.future_slots(
            startday.toPyDate(),
            sunday.toPyDate(),
            self.appt1_clinicians,
            busy_serialno=self.pt.serialno,
            override_emergencies=self.ignore_emergency_spaces)

        if self.app1_is_scheduled:
            self.set_primary_slots([])
        else:
            self.set_primary_slots(
                appointments.getLengthySlots(all_slots, self.app1_length))

        app2_slots = []
        if self.is_searching_for_double_appointments and \
                not self.app2_is_scheduled:
            all_slots = appointments.future_slots(
                startday.toPyDate(),
                sunday.toPyDate(),
                self.appt2_clinicians,
                busy_serialno=self.pt.serialno,
                override_emergencies=self.ignore_emergency_spaces)
            self.set_secondary_slots(
                appointments.getLengthySlots(all_slots,
                                             self.app2_length)
            )
            app1_slots = set([])
            if self.app1_is_scheduled:
                iterset = [self.appointment_model.currentAppt.to_freeslot()]
            else:
                iterset = self.primary_slots
            for app1_slot in iterset:
                for app2_slot in self.secondary_slots:
                    wait = app1_slot.wait_time(self.app1_length,
                                               self.app2_length,
                                               app2_slot)
                    if wait is not None and wait <= MAX_WAIT:
                        app2_slots.append(app2_slot)
                        app1_slots.add(app1_slot)
            if not self.app1_is_scheduled:
                self.set_primary_slots(app1_slots)

        self.set_secondary_slots(app2_slots)

    @property
    def chosen_2nd_slots(self):
        if not (self.appointment_model.currentAppt is None or
                self.appointment_model.secondaryAppt is None):
            for app2_slot in self.secondary_slots:
                wait = self.chosen_slot.wait_time(self.app1_length,
                                                  self.app2_length,
                                                  app2_slot)
                if wait is not None and wait <= MAX_WAIT:
                    yield app2_slot
        else:
            LOGGER.debug("no appointments selected")

    @property
    def last_appt_date(self):
        '''
        returns the latest date of patient's appointments,
        or today's date if none found
        '''
        last_d = QtCore.QDate.currentDate().toPyDate()
        for appt in self.appointment_model.scheduledList:
            if appt.date > last_d:
                last_d = appt.date
        return last_d

    @property
    def is_searching(self):
        '''
        are we looking for a slot?
        '''
        app1 = self.appointment_model.currentAppt
        if app1 is not None and app1.unscheduled:
            return True
        app2 = self.appointment_model.secondaryAppt
        if app2 is not None and app2.unscheduled:
            return True
        return False

    @property
    def is_searching_for_double_appointments(self):
        return self.appointment_model.secondaryAppt is not None

    @property
    def search_again(self):
        '''
        this determines whether it is worth continuing (on a different date)
        '''
        return (self.is_searching and
                self.search_mode != self.NOT_SEARCHING and
                len(self.selectedClinicians) > 0 and
                len(self.primary_slots) == 0)

    def find_first_appointment(self):
        self.show_first_appointment.emit()

    @property
    def chosen_slot(self):
        if self.primary_slots == []:
            if self.app1_is_scheduled:
                return self.appointment_model.currentAppt.to_freeslot()
            return None
        if self._chosen_slot is None:
            if self.searching_past:
                self._chosen_slot = self.primary_slots[-1]
            else:
                self._chosen_slot = self.primary_slots[0]
        return self._chosen_slot

    def set_chosen_slot(self, slot):
        self._chosen_slot = slot

    def set_chosen_2nd_slot(self, slot):
        '''
        user has clicked on a secondary slot - we need to switch the
        appointments over!
        '''
        LOGGER.debug("set_chosen_2nd_slot %s", slot)
        model = self.appointment_model.selection_model
        selection = model.selection()
        selection.swap(0, 1)
        model.select(selection, model.ClearAndSelect)
        self.selection_changed(
            self.appointment_model.selection_model.selection())
        self.appointment_model.selection_model.emitSelectionChanged(
            selection, QtGui.QItemSelection())
        slot.is_primary = True
        self.set_chosen_slot(slot)
        self.chosen_slot_changed.emit()

    @property
    def excluded_days(self):
        return ApptSettingsDialog.excluded_days

    def show_pt_diary(self):
        if self.pt is None:
            QtGui.QMessageBox.information(self, _("error"),
                                          _("No patient selected"))
            return

        def _find_appt(appt):
            dl.accept()
            self.find_appt.emit(appt)

        def _start_scheduling():
            dl.accept()
            self.get_data()
            self.appointment_model.selection_model.reset()
            appts = pt_diary_widget.selected_appointments
            self.update_appt_selection(appts)
            QtCore.QTimer.singleShot(100, self.start_scheduling.emit)

        pt_diary_widget = PtDiaryWidget()
        pt_diary_widget.find_appt.connect(_find_appt)
        pt_diary_widget.start_scheduling.connect(_start_scheduling)

        pt_diary_widget.set_patient(self.pt)

        dl = QtGui.QDialog(self)
        but_box = QtGui.QDialogButtonBox(dl)
        but = but_box.addButton(_("Close"), but_box.AcceptRole)
        but.clicked.connect(dl.accept)

        layout = QtGui.QVBoxLayout(dl)
        layout.addWidget(pt_diary_widget)
        layout.addStretch()
        layout.addWidget(but_box)

        dl.exec_()

        self.appointment_model.load_from_database(self.pt)
        self.enable_scheduling_buttons()

    def enable_scheduling_buttons(self):
        enabled = self.is_searching
        for but in (self.next_appt_button,
                    self.next_day_button,
                    self.prev_appt_button,
                    self.prev_day_button,
                    self.first_appt_button):
            but.setEnabled(enabled)
        self.update_search_criteria_webview()

    def begin_make_appointment(self):
        '''
        this is when an external widget calls for us to start the process
        of starting an appointment
        '''
        self.set_mode(self.SCHEDULE_MODE)
        self.enable_scheduling_buttons()
        LOGGER.debug("checking appointment settings %s",
                     ApptSettingsDialog.is_default_settings())
        if not ApptSettingsDialog.is_default_settings():
            dl = ApptSettingsResetDialog(self)
            if dl.exec_():
                if dl.show_settings_dialog:
                    self.show_settings_dialog()
                else:
                    ApptSettingsDialog.reset()

    def check_schedule_status(self, automatic):
        '''
        this is called by the diary widget when the books have been laid out
        whilst in schedule mode.
        Inform the user
        '''
        assert self.mode == self.SCHEDULE_MODE, "not in schedule mode"
        LOGGER.debug(
            "check_schedule_status %s", self.diary_widget.selected_date())
        if automatic:
            # this has been called by a timer update to the diary,
            # and therefore NOT user interaction
            LOGGER.debug("automatic call to check_schedule_status... ignoring")
            return

        try:
            date_ = self.diary_widget.selected_date().toPyDate()
        except AttributeError:  # self.diary_widget is None?
            LOGGER.debug("date check error", exc_info=1)
            date_ = localsettings.currentDay()

        if not self.appointment_model.selectedAppts:
            self.advice_signal.emit(
                _("Please select an appointment to begin scheduling"), 0)
        elif self.app1_is_scheduled:
            if self.appointment_model.secondaryAppt is None:
                self.advice_signal.emit(
                    _("appointment is already scheduled"), 0)
            elif self.app2_is_scheduled:
                self.advice_signal.emit(_("Joint appointment Scheduled"), 0)
            elif not list(self.chosen_2nd_slots):
                self.advice_signal.emit(
                    _("Joint appointment is not possible with the "
                      "chosen primary appointment"), 1)
        elif self.search_again:
            LOGGER.debug("automatic searching")
            if date_ > localsettings.BOOKEND:
                self.advice_signal.emit(
                    u'''<b>%s<br />%s</b><hr /><em>(%s)</em>
                    <ul>
                    <li>%s</li><li>%s</li><li>%s</li><li>%s</li>
                    </ul>''' % (
                        _("This date is beyond the diary limit."),
                        _("Please search again with different criteria."),
                        _("for instance..."),
                        _("no excluded days"),
                        _("ignore emergencies"),
                        _("add or view more clinicians"),
                        _("or you have requested an impossible appointment!")),
                    1)
                self.cancel_search_mode()
                self.diary_widget.set_date(localsettings.currentDay())
            elif date_ < localsettings.currentDay():
                self.advice_signal.emit(
                    _("You can't schedule an appointment in the past"),
                    1)
                self.diary_widget.set_date(localsettings.currentDay())
            else:
                self.diary_widget.step_date(self.searching_future)
        elif date_ > localsettings.BOOKEND:
            self.advice_signal.emit(
                _("This date is beyond the diary limit."), 1)
        elif date_ < localsettings.currentDay():
            self.advice_signal.emit(
                _("You can't schedule an appointment in the past"), 1)
            self.diary_widget.set_date(localsettings.currentDay())
        elif self.chosen_slot is None and not list(self.chosen_2nd_slots):
            if self.diary_widget:
                if self.diary_widget.viewing_week:
                    message = "%s %s" % (
                        _("in this week"),
                        self.diary_widget.selected_date().weekNumber())
                else:
                    message = "%s (%s)" % (
                        _("on this day"),
                        localsettings.formatDate(
                            self.diary_widget.selected_date().toPyDate())
                    )
            else:
                message = ""  # should only happen if __name__ == "__main__"
            message = "%s %s" % (_("No Slots Found"), message)
            self.advice_signal.emit(message, 0)

    @property
    def _dentist_message(self):
        if not self.appointment_model.dentists_involved:
            return ""
        if ApptSettingsDialog.dentist_policy == \
                ApptSettingsDialog.CLINICIAN_SELECTED:
            return _("Specified Dentist only")
        elif ApptSettingsDialog.dentist_policy == \
                ApptSettingsDialog.CLINICIAN_ANY_DENT:
            return _("Any Dentist")
        else:  # CLINICIAN_ANY
            return _("Any Clinician")

    @property
    def _hygienist_message(self):
        if not self.appointment_model.hygienists_involved:
            return ""
        if ApptSettingsDialog.hygienist_policy == \
                ApptSettingsDialog.CLINICIAN_SELECTED:
            return _("Specified Hygienist only for hyg appts")
        if ApptSettingsDialog.hygienist_policy == \
                ApptSettingsDialog.CLINICIAN_ANY_HYG:
            return _("Any Hygienist for hyg appts")
        else:  # CLINICIAN_ANY
            return _("Any Clinician for hyg appts")

    @property
    def _joint_message(self):
        if self.is_searching_for_double_appointments:
            return _("Joint Appointments")
        return ""

    @property
    def _emergency_message(self):
        if ApptSettingsDialog.ignore_emergency_spaces:
            return "%s" % _("Overwrite Emergencies")
        return ""

    @property
    def _day_message(self):
        if self.excluded_days == []:
            return _("Any Day")
        days = []
        for i, day in enumerate(
            (_("Mon"), _("Tue"), _("Wed"), _("Thu"),
             _("Fri"), _("Sat"), _("Sun")), 1):
            if i not in self.excluded_days:
                days.append(day)
        return ", ".join(days)

    def update_search_criteria_webview(self):
        if self.appointment_model.currentAppt is None:
            html = _("No Appointment Selected")
        else:
            html = '%s<ul><li>%s</li></ul>' % (
                _("Search Settings"),
                "</li><li>". join(
                    [s for s in (
                        self._dentist_message,
                        self._hygienist_message,
                        self._joint_message,
                        self._emergency_message,
                        self._day_message) if s != ""])
            )
        self.search_criteria_webview.setHtml(html)

    def update_highlighted_appointment(self):

        '''
        the diary widget selected appointment has changed.
        '''
        app = self.diary_widget.highlighted_appointment
        LOGGER.debug("appointment highlighted %s", app)
        if app is None:
            self.reset_browsing_webview()
            return
        if self.mode != self.BROWSE_MODE:
            return

        feedback = FEEDBACK % (
            app.name, app.serialno,
            localsettings.readableDate(
                self.diary_widget.selected_date().toPyDate()),
            "%02d:%02d" % (app.start // 100, app.start % 100),
            "%02d:%02d" % (app.end // 100, app.end % 100),
            '</li><li class="trt">'.join(
                [val for val in (app.trt1, app.trt2, app.trt3) if val != ""])
        )
        if app.memo != "":
            feedback += "<hr />%s<br /><i>%s</i>" % (_("Memo"), app.memo)
        try:
            datestamp = app.timestamp.date()
            feedback += \
                "<hr />%s<br />%s (%s %s)" % (
                    _("Made"),
                    localsettings.formatDate(datestamp),
                    _("at"),
                    localsettings.pyTimeToHumantime(
                        app.timestamp))
        except AttributeError:
            pass
        if app.mh_form_check_date or app.mh_form_required:
            feedback += "<hr />"
        if app.mh_form_check_date:
            feedback += "%s %s<br />" % (
                _("last mh form"),
                localsettings.formatDate(
                    app.mh_form_check_date)
            )
        if app.mh_form_required:
            feedback += "%s" % _("MH CHECK REQUIRED")

        feedback = "%s<body></html>" % feedback
        self.browsing_webview.setHtml(feedback)


class TestWindow(QtGui.QMainWindow):
    MODES = ("Browse", "Schedule", "Block", "Notes")

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.schedule_controller = DiaryScheduleController()
        pt = BriefPatient(1)
        self.schedule_controller.set_patient(pt)

        self.but = QtGui.QPushButton()
        self.but.clicked.connect(self.change_mode)
        self.text_browser = QtGui.QTextBrowser()

        self.mode = self.schedule_controller.BROWSE_MODE

        frame = QtGui.QFrame()
        layout = QtGui.QGridLayout(frame)
        layout.addWidget(self.schedule_controller, 0, 0, 2, 1)
        layout.addWidget(self.but, 1, 1)
        layout.addWidget(self.text_browser, 0, 1)

        self.set_but_text()

        self.setCentralWidget(frame)

        self.schedule_controller.appointment_selected.connect(
            self.sig_catcher)
        self.schedule_controller.patient_selected.connect(self.sig_catcher)
        self.schedule_controller.show_first_appointment.connect(
            self.sig_catcher)
        self.schedule_controller.chosen_slot_changed.connect(self.sig_catcher)
        self.schedule_controller.find_appt.connect(self.sig_catcher)
        self.schedule_controller.start_scheduling.connect(self.sig_catcher)
        self.change_mode()

    def sizeHint(self):
        return QtCore.QSize(400, 500)

    def set_but_text(self):
        self.but.setText("set mode (current='%s')" % self.MODES[self.mode])

    def change_mode(self):
        '''
        toggle through the modes
        '''
        self.mode += 1
        if self.mode > self.schedule_controller.NOTES_MODE:
            self.mode = self.schedule_controller.BROWSE_MODE

        self.set_but_text()
        self.text_browser.setHtml("")
        self.schedule_controller.set_mode(self.mode)

    def sig_catcher(self, *args):
        LOGGER.info("signal emitted %s", args)

        html = "<h4>Selected Clinicians</h4><ul><li>"
        html += "</li><li>".join(
            [str(i) for i in self.schedule_controller.selectedClinicians])
        html += "</li></ul>"

        html += "<h4>Involved Clinicians</h4><ul><li>"
        html += "</li><li>".join(
            [str(i) for i in self.schedule_controller.involvedClinicians])
        html += "</li></ul>"

        html += "<h4>Main Appointment</h4>%s<br /><br />" % \
            self.schedule_controller.selected_appointment
        html += "slot length = %s" % self.schedule_controller.app1_length
        html += "<br />make with %s" % str(
            self.schedule_controller.appt1_clinicians)

        html += "<h4>Secondary Appointment</h4>%s<br /><br />" % \
            self.schedule_controller.secondary_appointment
        html +=  \
            "slot length = %s" % self.schedule_controller.app2_length
        html += "<br />make with %s" % str(
            self.schedule_controller.appt2_clinicians)

        self.text_browser.setHtml(html)


if __name__ == "__main__":

    LOGGER.setLevel(logging.DEBUG)
    localsettings.initiate()

    app = QtGui.QApplication([])
    obj = TestWindow()
    obj.show()
    app.exec_()
