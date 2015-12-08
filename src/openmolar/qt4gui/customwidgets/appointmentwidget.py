#! /usr/bin/env python
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
provides one class - the appointment widget
the canvas is a subclass of this
'''

from __future__ import division

import datetime
from functools import partial
from gettext import gettext as _
import logging
import pickle

from PyQt4 import QtGui, QtCore
from openmolar.settings import localsettings
from openmolar.qt4gui import colours
from openmolar.qt4gui.dialogs import blockslot

LOGGER = logging.getLogger("openmolar")

BGCOLOR = QtCore.Qt.transparent
FREECOLOR = colours.APPT_Background
LINECOLOR = colours.APPT_LINECOLOUR
APPTCOLORS = colours.APPTCOLORS
TRANSPARENT = colours.TRANSPARENT

BLACK_PEN = QtGui.QPen(QtCore.Qt.black, 1)
GREY_PEN = QtGui.QPen(QtCore.Qt.gray, 1)
RED_PEN = QtGui.QPen(QtCore.Qt.red, 2)
BIG_RED_PEN = QtGui.QPen(QtCore.Qt.red, 4)
BLUE_PEN = QtGui.QPen(QtCore.Qt.blue, 2)

CENTRE_OPTION = QtGui.QTextOption(QtCore.Qt.AlignCenter)
CENTRE_OPTION.setWrapMode(QtGui.QTextOption.WordWrap)


class AppointmentWidget(QtGui.QFrame):

    '''
    a custom widget to for a dental appointment book
    useage is (startTime,finishTime, parentWidget - optional)
    startTime,finishTime in format HHMM or HMM or HH:MM or H:MM
    slotDuration is the minimum slot length - typically 5 minutes
    textDetail is the number of slots to draw before writing the time text
    parentWidget =optional
    '''
    selected_serialno = None
    BROWSING_MODE = 0
    SCHEDULING_MODE = 1
    mode = None

    # signal has dent, time, length
    slot_clicked_signal = QtCore.pyqtSignal(object)
    print_mh_signal = QtCore.pyqtSignal(object)
    mh_form_date_signal = QtCore.pyqtSignal(object)
    new_memo_signal = QtCore.pyqtSignal(object, object)
    block_empty_slot_signal = QtCore.pyqtSignal(object)
    cancel_appointment_signal = QtCore.pyqtSignal(object, object, object)
    clear_slot_signal = QtCore.pyqtSignal(object, object, object)

    def __init__(self, sTime, fTime, om_gui):
        QtGui.QFrame.__init__(self, om_gui)

        self.header_frame = QtGui.QFrame(self)
        self.om_gui = om_gui
        self.printButton = QtGui.QPushButton("", self.header_frame)
        self.printButton.setMaximumWidth(50)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/ps.png"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.printButton.setIcon(icon)

        self.connect(self.printButton, QtCore.SIGNAL("clicked()"),
                     self.printme)

        self.header_label = QtGui.QLabel("dent", self.header_frame)
        self.header_label.setAlignment(QtCore.Qt.AlignCenter)

        font = QtGui.QFont("Sans", 14, 75)
        self.header_label.setFont(font)

        self.memo_lineEdit = QtGui.QLineEdit(self)
        self.memo_lineEdit.setText("hello")
        self.memo_lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.memo_lineEdit.setMaxLength(30)  # due to schema restrictions :(

        font = QtGui.QFont("Sans", 12, 75, True)
        self.memo_lineEdit.setFont(font)
        # self.memo_lineEdit.setStyleSheet("background:white")

        self.dentist = "DENTIST"
        self.apptix = 0
        glay = QtGui.QGridLayout(self.header_frame)
        glay.setSpacing(2)
        glay.setMargin(2)
        glay.addWidget(self.printButton, 0, 1)
        glay.addWidget(self.header_label, 0, 0)
        glay.addWidget(self.memo_lineEdit, 1, 0, 1, 2)

        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidgetResizable(True)

        self.canvas = AppointmentCanvas(om_gui, self)
        self.scrollArea.setWidget(self.canvas)

        self.setDayStartTime(sTime)
        self.setStartTime(sTime)
        self.setDayEndTime(fTime)
        self.setEndTime(fTime)

        self.OOlabel = QtGui.QLabel(_("Out Of Office"))
        self.OOlabel.setWordWrap(True)
        self.OOlabel.setAlignment(QtCore.Qt.AlignCenter)
        self.OOlabel.setSizePolicy(QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        lay = QtGui.QVBoxLayout(self)
        lay.setSpacing(0)
        lay.setMargin(2)
        lay.addWidget(self.header_frame)
        lay.addWidget(self.OOlabel)
        lay.addWidget(self.scrollArea)

        self.outofoffice = False
        self.setOutOfOffice(False)

        self.setMinimumSize(self.minimumSizeHint())
        # self.setMaximumSize(self.maximumSizeHint())
        self.signals()

    def setOutOfOffice(self, val):
        '''
        toggle out of office
        '''
        self.outofoffice = val
        self.OOlabel.setVisible(val)
        self.scrollArea.setVisible(not val)

    def setDentist(self, apptix):
        '''
        update the dentist the widget relates to
        '''
        self.apptix = apptix
        self.dentist = localsettings.apptix_reverse.get(apptix, "??")

    def sizeHint(self):
        '''
        set an (arbitrary) size for the widget
        '''
        return QtCore.QSize(200, 400)

    def minimumSizeHint(self):
        '''
        set an (arbitrary) minimum size for the widget
        '''
        return QtCore.QSize(120, 300)

    def maximumSizeHint(self):
        '''
        widget looks daft if too wide
        '''
        return QtCore.QSize(500, 16777215)

    def setDayStartTime(self, sTime):
        '''
        a public method to set the Practice Day Start
        '''
        self.canvas.setDayStartTime(sTime)

    def setDayEndTime(self, fTime):
        '''
        a public method to set the Practice Day End
        '''
        self.canvas.setDayEndTime(fTime)

    def setStartTime(self, sTime):
        '''
        a public method to set the earliest appointment available
        '''
        self.canvas.setStartTime(sTime)

    def setEndTime(self, fTime):
        '''
        a public method to set the end of the working day
        '''
        self.canvas.setEndTime(fTime)

    def setCurrentTime(self, t):
        '''
        send it a value like "HHMM" or "HH:MM" to draw a marker at that time
        '''
        return self.canvas.setCurrentTime(t)

    def clearAppts(self):
        '''
        resets - the widget values - DOES NOT REDRAW THE WIDGET
        '''
        self.canvas.appts = []
        self.canvas.doubleAppts = []
        self.canvas.rows = {}
        self.canvas.freeslots = []
        self.clear_active_slots()

    def clear_active_slots(self):
        self.canvas.active_slots = []

    def printme(self):
        '''
        emits a signal when the print button is clicked
        '''
        self.emit(QtCore.SIGNAL("print_me"), self.apptix)

    def newMemo(self):
        '''
        user has edited the memo line Edit - emit a signal so the
        gui can handle it
        '''
        if not self.memo_lineEdit.hasFocus():
            self.new_memo_signal.emit(
                self.dentist,
                unicode(self.memo_lineEdit.text().toUtf8(), "utf8", "ignore")
            )

    def signals(self):
        '''
        set up the widget's signals and slots
        '''
        self.connect(self.memo_lineEdit,
                     QtCore.SIGNAL("editingFinished()"), self.newMemo)

    def showEvent(self, event=None):
        if self.om_gui.pt:
            self.selected_serialno = self.om_gui.pt.serialno
        else:
            self.selected_serialno = None

    def update(self):
        if not self.outofoffice:
            self.canvas.update()

    def setAppointment(self, app):
        '''
        adds an appointment to the widget dictionary of appointments
        typical useage is instance.setAppointment
        ("0820","0900","NAME","serialno","trt1",
        "trt2","trt3","Memo", modtime)
        NOTE - this also appts to the widgets
        dictionary which has
        row number as key, used for signals when appts are clicked

        (5, 915, 930, 'MCPHERSON I', 6155L, 'EXAM', '', '', '', 1, 73, 0, 0,
        timestamp)
        (5, 1100, 1130, 'EMERGENCY', 0L, '', '', '', '', -128, 0, 0, 0,
        timestamp)
        '''

        app.startcell = self.canvas.getCell_from_time(str(app.start))
        app.endcell = self.canvas.getCell_from_time(str(app.end))
        if app.endcell == app.startcell:  # double and family appointments!!
            app.endcell += 1
            self.canvas.doubleAppts.append(app)
        else:
            self.canvas.appts.append(app)
        if app.serialno == 0:
            app.serialno = self.canvas.duplicateNo
            self.canvas.duplicateNo -= 1
        for row in range(app.startcell, app.endcell):
            if row in self.canvas.rows:
                self.canvas.rows[row].append(app.serialno)
            else:
                self.canvas.rows[row] = [app.serialno]

    def addSlot(self, slot):
        '''
        adds a slot to the widget's data
        '''
        if slot.dent != self.apptix:
            return
        self.canvas.freeslots.append(slot)

    def set_active_slot(self, slot):
        '''
        returns true if the slot is accepted
        (ie.. this book is for that dentist)
        '''
        if slot is not None and slot.dent == self.apptix:
            startcell = self.canvas.getCell_from_mpm(slot.mpm)
            endcell = self.canvas.getCell_from_mpm(slot.mpm_end)
            self.canvas.active_slots.append((startcell, endcell))

            self.canvas.ensure_slot_visible = True
            return True
        return False

    def enable_slots(self, bool_):
        self.canvas.enabled_slots = (
            bool_ or self.canvas.active_slots != [])

    def set_scroll_bar(self, scroll_bar):
        self.scrollArea.setVerticalScrollBar(scroll_bar)

    def scroll_bar_off(self):
        policy = QtCore.Qt.ScrollBarAlwaysOff
        self.scrollArea.setVerticalScrollBarPolicy(policy)

    def cancel_appt(self, snos, time, apptix):
        self.cancel_appointment_signal.emit(snos, time, apptix)


class BlinkTimer(QtCore.QTimer):
    '''
    A singleton shared accross all canvas widgets to ensure flashing
    appointments are synchronised.
    '''
    _instance = None
    _initiated = False
    state = True

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(
                BlinkTimer, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, parent=None):
        if not self._initiated:
            super(BlinkTimer, self).__init__(parent)
            self.start(1000)
            self.timeout.connect(self._toggle)
            self._initiated = True

    def _toggle(self):
        self.state = not self.state


class AppointmentCanvas(QtGui.QWidget):

    '''
    the canvas for me to draw on
    '''
    blink_on = True  # a boolean which toggles value

    enabled_slots = True
    ensure_slot_visible = True

    def __init__(self, om_gui, pWidget):
        QtGui.QWidget.__init__(self, pWidget)
        self.setSizePolicy(QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        self.setMinimumSize(self.minimumSizeHint())
        self.pWidget = pWidget
        self.slotDuration = 5  # 5 minute slots
        self.textDetail = 3   # time printed every 3 slots
        self.slotNo = 12
        self.dayEndTime = 60
        self.dayStartTime = 0
        self.startTime = 0
        self.endTime = 60
        self.appts = []
        self.freeslots = []
        self.doubleAppts = []
        self.rows = {}
        self.setTime = None
        self.selected_rows = (0, 0)
        self.setMouseTracking(True)
        self.duplicateNo = -1  # use this for serialnos =0
        self.om_gui = om_gui
        self.dragging = False
        self.drag_appt = None
        self.drop_time = None
        self.setAcceptDrops(True)
        self.qmenu = None
        self.mouse_freeslot = None
        self.active_slots = []

        self.font = QtGui.QFont(self.fontInfo().family(),
                                localsettings.appointmentFontSize)

        self.fm = QtGui.QFontMetrics(self.font)
        self.timeWidth = self.fm.width(" 88:88 ")
        self.slotHeight = self.fm.height() / self.textDetail

        self.blink_timer = BlinkTimer()
        self.blink_timer.timeout.connect(self.toggle_blink)

    def setDayStartTime(self, sTime):
        '''
        a public method to set the Practice Day Start
        '''
        self.dayStartTime = self.minutesPastMidnight(sTime)

    def setDayEndTime(self, fTime):
        '''
        a public method to set the Practice Day End
        '''
        self.dayEndTime = self.minutesPastMidnight(fTime)
        self.calcSlotNo()

    def setStartTime(self, sTime):
        '''
        a public method to set the earliest appointment available
        '''
        self.startTime = self.minutesPastMidnight(sTime)
        self.firstSlot = self.getCell_from_time(sTime) + 1

    def setEndTime(self, fTime):
        '''
        a public method to set the end of the working day
        '''
        self.endTime = self.minutesPastMidnight(fTime)
        self.lastSlot = self.getCell_from_time(fTime)

    def calcSlotNo(self):
        '''
        work out how many 'slots' there are given the lenght of day
        and length of slots
        '''
        self.slotNo = (
            self.dayEndTime - self.dayStartTime) // self.slotDuration
        self.slotHeight = self.fm.height() / self.textDetail

        min_height_required = self.slotHeight * self.slotNo

        if min_height_required < self.pWidget.scrollArea.height() * .98:
            self.setMinimumHeight(self.pWidget.scrollArea.height() * .98)
            self.slotHeight = self.height() / self.slotNo
        else:
            self.setMinimumHeight(min_height_required)

    def resizeEvent(self, event):
        self.calcSlotNo()

    def minutesPastMidnight(self, t):
        '''
        converts a time in the format of
        'HHMM' or 'H:MM' (both strings) to minutes
        past midnight
        '''
        hour, minute = int(t) // 100, int(t) % 100
        return hour * 60 + minute

    def humanTime(self, t):
        '''
        converts minutes past midnight(int) to format "HH:MM"
        '''
        hour, minute = t // 60, int(t) % 60
        return "%s:%02d" % (hour, minute)

    def setslotDuration(self, arg):
        '''
        set the slotDuration (default is 5 minutes)
        '''
        self.slotDuration = arg

    def setTextDetail(self, arg):
        '''
        set the number of rows between text time slots
        '''
        self.textDetail = arg

    def sizeHint(self):
        '''
        set an (arbitrary) size for the widget
        '''
        return QtCore.QSize(200, 500)

    def minimumSizeHint(self):
        '''
        set an (arbitrary) minimum size for the widget
        '''
        return QtCore.QSize(100, 200)

    def setCurrentTime(self, t):
        '''
        send it a value like "HHMM" or "HH:MM" to draw a marker at that time
        '''
        self.setTime = t
        if t and self.startTime < self.minutesPastMidnight(t) < self.endTime:
            return True

    def qTime(self, t):
        '''
        converts minutes past midnight(int) to a QTime
        '''
        hour, minute = t // 60, int(t) % 60
        return QtCore.QTime(hour, minute)

    def getCell_from_time(self, t):
        '''
        send a time - return the row number of that time
        '''
        return self.getCell_from_mpm(self.minutesPastMidnight(t))

    def getCell_from_mpm(self, mpm):
        '''
        send a time - return the row number of that time
        '''
        return (mpm - self.dayStartTime) // self.slotDuration

    def getTime_from_Cell(self, row):
        '''
        you know the row.. what time is that
        '''
        mpm = self.slotDuration * row + self.dayStartTime
        return localsettings.minutesPastMidnightToPyTime(mpm)

    def getPrev(self, arg):
        '''
        what slot is the previous appt?
        '''
        lower = arg
        while lower >= self.firstSlot:
            if lower in self.rows:
                lower += 1
                break
            lower -= 1
        return lower

    def getNext(self, arg):
        '''
        what slot is the next appt?
        '''
        upper = arg
        while upper < self.lastSlot:
            if upper in self.rows:
                break
            upper += 1
        return upper

    def getApptBounds(self, row, patients):
        '''
        get the start and finish of an appt
        this is complicated because the same patient may have 2 appointments
        on one day
        '''
        row_list = sorted(self.rows.keys())[:]
        start_row, end_row = row, row

        chk_row = row
        while chk_row >= row_list[0]:
            chk_row -= 1
            if self.rows.get(chk_row) == patients:
                start_row = chk_row
            else:
                break

        chk_row = row
        while chk_row <= row_list[-1]:
            chk_row += 1
            if self.rows.get(chk_row) == patients:
                end_row = chk_row
            else:
                break

        return (start_row, end_row+1)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-appointment"):
            data = event.mimeData()
            bstream = data.retrieveData("application/x-appointment",
                                        QtCore.QVariant.ByteArray)
            self.drag_appt = pickle.loads(bstream.toByteArray())

            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-appointment"):

            y = event.pos().y()
            yOffset = self.height() / self.slotNo
            self.drag_startrow = int(y // yOffset)

            if (self.drag_startrow < self.firstSlot - 1 or
               self.drag_startrow >= self.lastSlot or
               self.drag_startrow in self.rows):
                allowDrop = False
            else:
                n_rows = self.drag_appt.length // self.slotDuration
                self.drag_endrow = self.drag_startrow + n_rows
                # see if there's a long enough slot either side of the selected
                # row
                allowDrop = True
                for row in range(self.drag_startrow, self.drag_endrow):
                    if row in self.rows or row >= self.lastSlot:
                        allowDrop = False
                        break
                if not allowDrop:
                    allowDrop = True
                    self.drag_startrow = row - n_rows
                    self.drag_endrow = row
                    for row in range(self.drag_startrow, row):
                        if row in self.rows or row < self.firstSlot - 1:
                            allowDrop = False
                            break

            if allowDrop:
                self.dragging = True
                self.drop_time = self.getTime_from_Cell(self.drag_startrow)
                self.update()
                event.accept()
            else:
                self.dragging = False
                self.update()
                event.ignore()
        else:
            self.update()
            event.accept()

    def dragLeaveEvent(self, event):
        self.dragging = False
        self.update()
        event.accept()

    def dropEvent(self, event):
        self.dragging = False
        self.emit(QtCore.SIGNAL("ApptDropped"), self.drag_appt,
                  self.drop_time, self.pWidget.apptix)
        self.drag_appt = None
        self.dropOffset = 0
        event.accept()

    def mouse_over_freeslot(self, pos):
        self.mouse_freeslot = None
        for slot in self.freeslots:
            startcell = self.getCell_from_mpm(slot.mpm)
            endcell = self.getCell_from_mpm(slot.mpm_end)
            rect = QtCore.QRectF(
                self.timeWidth,
                startcell * self.slotHeight,
                self.width() - self.timeWidth,
                (endcell - startcell) * self.slotHeight)

            if rect.contains(QtCore.QPointF(pos)):
                self.mouse_freeslot = slot
                return True

    def mouseMoveEvent(self, event):
        y = event.y()
        yOffset = self.height() / self.slotNo
        row = int(y // yOffset)

        if not (self.firstSlot - 1) < row < self.lastSlot:
            self.selected_rows = (0, 0)
            self.update()
            self.setToolTip("")
            return

        if self.mouse_over_freeslot(event.pos()):
            startcell = self.getCell_from_mpm(self.mouse_freeslot.mpm)
            endcell = self.getCell_from_mpm(self.mouse_freeslot.mpm_end)
            feedback = '''<html><div align="center">
            <b>SLOT with %s</b><br />
            <b>%s</b><br />
            (%d mins)
            </div>
            </html>''' % (
                self.pWidget.dentist,
                self.getTime_from_Cell(startcell).strftime("%H:%M"),
                (endcell - startcell) * self.slotDuration,
            )
            self.setToolTip(feedback)
            self.selected_rows = (startcell, endcell)

        elif self.pWidget.mode == self.pWidget.BROWSING_MODE:
            feedback = ""
            if row in self.rows:
                sno_list = self.rows[row]
                self.selected_rows = self.getApptBounds(row, sno_list)
                self.update()

                for sno in sno_list:
                    if sno < 1:
                        continue
                    for app in self.appts + self.doubleAppts:
                        if app.serialno == sno:
                            feedback += '%s %s (%s)<br /><b>%s - %s</b>' % (
                                app.name, "&nbsp;" * 4, app.serialno,
                                app.start, app.end)
                            for val in (app.trt1, app.trt2, app.trt3):
                                if val != "":
                                    feedback += '''<br />
                                    <font color="red">%s</font>''' % val
                            if app.memo != "":
                                feedback += "<br /><i>%s</i>" % app.memo
                            try:
                                datestamp = app.timestamp.date()
                                moddate = localsettings.readableDate(datestamp)
                                if datestamp == localsettings.currentDay():
                                    feedback += \
                                        "<br /><i>%s %s %s %s</i><hr />" % (
                                            _("Made"), moddate, _("at"),
                                            localsettings.pyTimeToHumantime(
                                                app.timestamp))
                                else:
                                    feedback += \
                                        "<br /><i>%s<br />%s</i><hr />" % (
                                            _("Made on"), moddate)
                            except AttributeError:
                                feedback += "<hr />"
                            if app.mh_form_check_date:
                                feedback += "%s %s<br />" % (
                                    _("last mh form"),
                                    localsettings.formatDate(
                                        app.mh_form_check_date)
                                )
                            if app.mh_form_required:
                                feedback += "%s<hr />" % _("MH CHECK REQUIRED")

                if feedback:
                    feedback = "<html><body>%s</body></html>" % (
                        feedback[:feedback.rindex("r />") + 2])
            else:
                newSelection = (self.getPrev(row), self.getNext(row))
                if self.selected_rows != newSelection:
                    self.selected_rows = newSelection
                    self.update()
                start = int(
                    self.dayStartTime +
                    self.selected_rows[0] * self.slotDuration)
                finish = int(
                    self.dayStartTime +
                    self.selected_rows[1] * self.slotDuration)
                feedback = "%s %s" % (finish - start, _("Minutes Free"))

            self.setToolTip(feedback)
            if not feedback:
                QtGui.QToolTip.hideText()

    def mouseDoubleClickEvent(self, event):
        self.mousePressEvent(event)

    def mousePressEvent(self, event):
        '''
        catch the mouse press event -
        and if you have clicked on an appointment, emit a signal
        the signal has a LIST as argument -
        in case there are overlapping appointments or doubles etc...
        '''
        def singleClickMenuResult(result):
            if not result:
                return
            dent = localsettings.apptix.get(self.pWidget.dentist)
            if result.text() == _("Load Patient"):
                self.pWidget.emit(QtCore.SIGNAL("AppointmentClicked"),
                                  tuple(sno_list))
            elif result.text() == _("Add/Edit Memo"):
                self.pWidget.emit(QtCore.SIGNAL("EditAppointmentMemo"),
                                  tuple(sno_list), start, dent)
            elif result.text() == _("Cancel Appointment"):
                self.pWidget.cancel_appt(tuple(sno_list), start, dent)
            elif result.text() == _("Clear Block"):
                self.pWidget.clear_slot_signal.emit(start, finish, dent)
            elif result.text() == _("Block or use this space"):
                self.block_use_space(qstart, qfinish)
            elif result.text() == _("Print A Medical Form"):
                self.pWidget.print_mh_signal.emit(tuple(sno_list))
            elif result.text() == _("Save Medical Form Check Date"):
                self.pWidget.mh_form_date_signal.emit(tuple(sno_list))

        yOffset = self.height() / self.slotNo
        row = event.y() // yOffset

        actions = []

        if self.mouse_over_freeslot(event.pos()):
            self.pWidget.slot_clicked_signal.emit(self.mouse_freeslot)
            return
        elif self.selected_rows == (0, 0):
            return
        elif row in self.rows:
            start = self.humanTime(int(
                self.dayStartTime + self.selected_rows[0] * self.slotDuration))

            finish = self.humanTime(int(
                self.dayStartTime + self.selected_rows[1] * self.slotDuration))

            sno_list = self.rows[row]
            # ignore lunch and emergencies - serialno number is positive

            if sno_list[0] > 0:
                actions.append(_("Load Patient"))

                actions.append(None)
                actions.append(_("Add/Edit Memo"))
                actions.append(_("Cancel Appointment"))
                actions.append(None)
                actions.append(_("Save Medical Form Check Date"))
                actions.append(_("Print A Medical Form"))

                self.pWidget.emit(QtCore.SIGNAL("PatientClicked"),
                                  tuple(sno_list))
            else:
                actions.append(_("Clear Block"))
        else:
            # no-one in the book...
            qstart = self.qTime(int(
                self.dayStartTime + self.selected_rows[0] * self.slotDuration))
            qfinish = self.qTime(int(
                self.dayStartTime + self.selected_rows[1] * self.slotDuration))
            if (self.firstSlot - 1) < row < self.lastSlot:
                actions.append(_("Block or use this space"))

        if self.qmenu and event.type() == QtCore.QEvent.MouseButtonDblClick:
            singleClickMenuResult(self.qmenu.defaultAction())
            self.qmenu.clear()
            return

        self.qmenu = QtGui.QMenu(self)
        for i, action in enumerate(actions):
            if action is None:
                self.qmenu.addSeparator()
                continue
            q_act = self.qmenu.addAction(action)
            if i == 0:
                self.qmenu.setDefaultAction(q_act)
        if event.button() == QtCore.Qt.RightButton:
            singleClickMenuResult(self.qmenu.exec_(event.globalPos()))

    def block_use_space(self, start, finish):
        Dialog = QtGui.QDialog(self)
        dl = blockslot.blockDialog(Dialog, self.om_gui)

        dl.setTimes(start, finish)
        dl.setPatient(self.om_gui.pt)

        if dl.exec_():
            adjstart = dl.start_timeEdit.time()
            adjfinish = dl.finish_timeEdit.time()
            if finish < start:
                QtGui.QMessageBox.information(self, _("Whoops!"),
                                              _("Bad Time Sequence!"))

            if dl.block:
                reason = str(
                    dl.comboBox.currentText().toAscii())[:30]
                args = (start, finish, adjstart, adjfinish,
                        localsettings.apptix.get(self.pWidget.dentist), reason)
                self.pWidget.block_empty_slot_signal.emit(args)
            else:
                reason = dl.reason_comboBox.currentText().toAscii()
                self.pWidget.emit(
                    QtCore.SIGNAL("Appointment_into_EmptySlot"),
                    (start, finish, adjstart, adjfinish,
                     localsettings.apptix.get(self.pWidget.dentist),
                     reason, dl.patient))

    def leaveEvent(self, event):
        self.mouse_down = False
        self.selected_rows = (0, 0)
        self.update()

    def paintEvent(self, event=None):
        '''
        draws the book - recalled at any point by instance.update()
        '''

        painter = QtGui.QPainter(self)

        painter.setFont(self.font)

        # define and draw the white boundary

        painter.setBrush(colours.APPT_Background)
        painter.setPen(QtGui.QPen(colours.APPT_Background, 1))

        top = (self.firstSlot - 1) * self.slotHeight
        bottom = (self.lastSlot + 1 - self.firstSlot) * self.slotHeight

        colwidth = self.width() - self.timeWidth
        mh_width = painter.fontMetrics().width("+")

        rect = QtCore.QRectF(self.timeWidth, top, colwidth, bottom)

        painter.drawRect(rect)

        # DRAW HORIZONTAL LINES AND TIMES

        for currentSlot in xrange(self.slotNo):
            textneeded = True if currentSlot % self.textDetail == 0 else False
            y = currentSlot * self.slotHeight
            # code to check if within the appointment hours
            if self.firstSlot <= currentSlot <= self.lastSlot:
                painter.setPen(QtGui.QPen(LINECOLOR, 1))
                painter.drawLine(self.timeWidth + 1, y, self.width() - 1, y)
            if textneeded:
                trect = QtCore.QRectF(0, y,
                                      self.timeWidth,
                                      y + self.textDetail * self.slotHeight)
                painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
                painter.drawLine(0, y, self.timeWidth, y)
                painter.drawText(
                    trect, QtCore.Qt.AlignLeft,
                    self.humanTime(
                        self.dayStartTime + (currentSlot * self.slotDuration)))

        # layout appts
        painter.save()
        painter.setPen(BLACK_PEN)

        selected_rect = None
        for app in self.appts:
            painter.save()
            rect = QtCore.QRectF(
                self.timeWidth, app.startcell * self.slotHeight,
                colwidth - painter.pen().width(),
                (app.endcell - app.startcell) * self.slotHeight)
            if (app.serialno != 0 and
                    app.serialno == self.pWidget.selected_serialno):
                painter.setBrush(QtGui.QColor("orange"))
            elif self.pWidget.mode == self.pWidget.SCHEDULING_MODE:
                painter.setBrush(APPTCOLORS["BUSY"])
                painter.setPen(GREY_PEN)
            elif app.cset in APPTCOLORS:
                painter.setBrush(APPTCOLORS[app.cset])
            elif app.name.upper() in APPTCOLORS:
                painter.setBrush(APPTCOLORS[app.name.upper()])
            elif app.flag0 == -128:
                painter.setBrush(APPTCOLORS["BUSY"])
            else:
                painter.setBrush(APPTCOLORS["default"])

            if not (app.serialno == 0 and
                    (app.endcell < self.firstSlot or
                     app.startcell > self.lastSlot)):
                painter.drawRoundedRect(rect, 5, 5)
                mytext = " ".join((app.name.title(), app.trt1, app.trt2,
                                   app.trt3, app.memo))

                painter.drawText(rect, mytext, CENTRE_OPTION)

            # highlight any appointments booked today
            if app.serialno > 0:
                if app.timestamp and \
                        app.timestamp.date() == localsettings.currentDay():
                    e_height = app.endcell - app.startcell
                    if e_height == 0:
                        e_height = 2
                    elif e_height > 5:
                        e_height = 5
                    e_rect = QtCore.QRectF(
                        self.width() - self.timeWidth / 2,
                        app.startcell * self.slotHeight,
                        self.timeWidth / 2,
                        self.slotHeight * e_height  # rect.height()
                    ).adjusted(2, 2, -2, -2)

                    painter.setPen(colours.BOOKED_TODAY)
                    painter.setBrush(colours.BOOKED_TODAY)
                    painter.drawEllipse(e_rect)

                if app.mh_form_required:
                    m_height = app.endcell - app.startcell
                    if m_height > 3:
                        m_height = 3
                    med_rect = QtCore.QRectF(
                        self.timeWidth,
                        app.startcell * self.slotHeight,
                        mh_width * 2,
                        self.slotHeight * m_height
                    ).adjusted(2, 2, 0, 0)
                    painter.setBrush(colours.APPT_MED_BACKGROUND)
                    painter.setPen(colours.APPT_Background)
                    painter.drawRect(med_rect)
                    painter.setPen(colours.APPT_MED_FORM)
                    painter.drawText(med_rect, "+", CENTRE_OPTION)

            if self.selected_rows == (app.startcell, app.endcell):
                selected_rect = rect

            painter.restore()
        painter.restore()

        painter.save()
        for appt in self.doubleAppts:
            rect = QtCore.QRectF(
                colwidth,
                app.startcell * self.slotHeight,
                colwidth,
                self.slotHeight)

            painter.setBrush(APPTCOLORS["DOUBLE"])
            painter.drawRect(rect)
        painter.restore()

        painter.save()
        for slot in self.freeslots:
            startcell = self.getCell_from_mpm(slot.mpm)
            endcell = self.getCell_from_mpm(slot.mpm_end)
            if slot.is_primary:
                brush = APPTCOLORS["SLOT"]
            else:
                brush = APPTCOLORS["SLOT2"]
            if (startcell, endcell) in self.active_slots:
                painter.setPen(BIG_RED_PEN)
                if self.blink_on:
                    painter.setOpacity(1)
                    # brush = APPTCOLORS["ACTIVE_SLOT_BOLD"]
                else:
                    painter.setOpacity(0.3)
                if self.ensure_slot_visible:
                    self.ensure_visible(0, startcell * self.slotHeight)
            else:
                painter.setPen(RED_PEN)
                painter.setOpacity(0.6)
            painter.setBrush(brush)
            rect = QtCore.QRectF(
                self.timeWidth + 1,
                startcell * self.slotHeight,
                colwidth - 3,
                (endcell - startcell) * self.slotHeight)
            painter.drawRoundedRect(rect, 5, 5)
            slot_duration = (endcell - startcell) * self.slotDuration
            painter.setOpacity(1)
            painter.drawText(rect, "%s mins" % slot_duration, CENTRE_OPTION)
        painter.restore()

        # highlight current time
        if self.setTime:
            cellno = self.getCell_from_time(self.setTime)
            painter.setPen(BLUE_PEN)
            painter.setBrush(QtCore.Qt.blue)
            corner1 = [self.timeWidth * 1.4, cellno * self.slotHeight]
            corner2 = [self.timeWidth, (cellno - 0.5) * self.slotHeight]
            corner3 = [self.timeWidth, (cellno + 0.5) * self.slotHeight]
            triangle = corner1 + corner2 + corner3
            painter.drawPolygon(QtGui.QPolygon(triangle))
            corner1 = [self.width() - self.timeWidth * 0.4,
                       cellno * self.slotHeight]
            corner2 = [self.width(), (cellno - 0.5) * self.slotHeight]
            corner3 = [self.width(), (cellno + 0.5) * self.slotHeight]
            triangle = corner1 + corner2 + corner3
            painter.drawPolygon(QtGui.QPolygon(triangle))

        if self.dragging:
            painter.setPen(RED_PEN)
            y = self.drag_startrow * self.slotHeight
            y2 = self.drag_endrow * self.slotHeight
            painter.drawLine(0, y, self.width(), y)
            painter.setBrush(QtGui.QColor("yellow"))

            trect = QtCore.QRectF(self.timeWidth, y,
                                  self.width() - self.timeWidth, y2 - y)
            painter.drawRect(trect)

            droptime = self.drop_time.strftime("%H:%M")
            trect = QtCore.QRectF(0, y, self.timeWidth, y2 - y)
            painter.drawRect(trect)
            painter.drawText(trect, QtCore.Qt.AlignHCenter, droptime)
        elif (selected_rect is None and
              self.selected_rows != (0, 0) and
              self.pWidget.mode == self.pWidget.BROWSING_MODE):
            startcell, endcell = self.selected_rows
            selected_rect = QtCore.QRectF(
                self.timeWidth + 1,
                startcell * self.slotHeight,
                colwidth - 3,
                (endcell - startcell) * self.slotHeight)
        if selected_rect:
            painter.setPen(QtGui.QPen(QtGui.QColor("red"), 3))
            painter.setBrush(QtGui.QBrush(BGCOLOR))
            painter.drawRect(selected_rect)

    def toggle_blink(self):
        if not self.pWidget.mode == self.pWidget.SCHEDULING_MODE:
            return
        self.blink_on = self.blink_timer.state
        self.update()

    def ensure_visible(self, x, y):
        QtCore.QTimer.singleShot(
            5,
            partial(self.pWidget.scrollArea.ensureVisible, x, y))


if __name__ == "__main__":
    from openmolar.dbtools import appointments
    from openmolar.dbtools.brief_patient import BriefPatient

    def clicktest(*args):
        print "clicktest", args

    import sys
    localsettings.initiate()
    app = QtGui.QApplication(sys.argv)

    # -initiate a book starttime 08:00 endtime 10:00
    # -five minute slots, text every 3 slots

    # from openmolar.qt4gui import maingui
    # parent = maingui.OpenmolarGui()
    parent = QtGui.QFrame()
    parent.pt = BriefPatient(1)

    form = AppointmentWidget("0800", "1500", parent)
    form.setStartTime("0830")
    form.setEndTime("1430")
    form.apptix = 5

    print'''
    created a calendar with start %d minutes past midnight
                1st appointment %d minutes past midnight
            appointments finish %d minutes past midnight
                        day end %d minutes past midnight
    - %d %d minutes slots''' % (
        form.canvas.dayStartTime,
        form.canvas.startTime,
        form.canvas.endTime,
        form.canvas.dayEndTime,
        form.canvas.slotNo,
        form.canvas.slotDuration)

    form.setCurrentTime("945")
    form.clearAppts()

    dt = datetime.datetime.now()
    for tup in (
        (5, 915, 930, 'MCDONALD I', 6155, 'EXAM', '', '', '', 1, 73, 0, 0,
         dt, dt.date()),
        (5, 1100, 1130, 'EMERGENCY', 0, '', '', '', '', -128, 0, 0, 0,
         dt, dt.date()),
        (5, 1300, 1400, 'LUNCH', 0, '', '', '', '', -128, 0, 0, 0,
         dt, dt.date()),
        (5, 1400, 1410, 'STAFF MEETING', 0, '', '', '', '', -128, 0, 0, 0,
         dt, dt.date()),
        (5, 930, 1005, 'TAYLOR J', 19373, 'FILL', '', '', '', 1, 80, 0, 0,
         dt, dt.date()),
        (5, 1210, 1230, 'TAYLOR J', 19373, 'FILL', '', '', '', 1, 80, 0, 0,
         dt, dt.date()),
    ):
        appt = appointments.Appointment(tup)
        form.setAppointment(appt)

    slot_date = datetime.datetime.combine(dt.date(), datetime.time(11, 30))
    slot = appointments.FreeSlot(slot_date, 5, 40)
    form.addSlot(slot)

    slot = appointments.FreeSlot(
        slot_date + datetime.timedelta(minutes=60), 5, 30)
    form.addSlot(slot)

    form.set_active_slot(slot)

    form.connect(form, QtCore.SIGNAL("AppointmentClicked"), clicktest)
    form.clear_slot_signal.connect(clicktest)
    form.block_empty_slot_signal.connect(clicktest)
    form.connect(form, QtCore.SIGNAL("print_me"), clicktest)
    form.connect(form, QtCore.SIGNAL("Appointment_into_EmptySlot"), clicktest)

    form.mode = form.SCHEDULING_MODE
    # form.mode = form.BROWSING_MODE

    v = QtGui.QVBoxLayout()
    v.setSpacing(0)
    v.addWidget(form)
    parent.setLayout(v)
    parent.show()

    sys.exit(app.exec_())
