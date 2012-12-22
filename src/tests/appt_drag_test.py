import datetime
import cPickle
import pickle
import sys

from PyQt4 import QtGui, QtCore
from openmolar.dbtools import appointments
from openmolar.settings import localsettings

from openmolar.qt4gui.appointment_gui_modules.draggable_list \
    import DraggableList
from openmolar.qt4gui.appointment_gui_modules.list_models \
    import SimpleListModel, BlockListModel


class _DragTestDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("Drag Drop Test")
        self.pt = duckPt()

        layout = QtGui.QGridLayout(self)

        self.model = SimpleListModel()

        appts = appointments.get_pts_appts(duckPt())

        self.model.set_appointments(appts, appts[1])

        self.appt_listView = DraggableList(True)
        self.appt_listView.setModel(self.model)

        self.block_model = BlockListModel()
        self.blockView = DraggableList(False)
        self.blockView.setModel(self.block_model)

        self.book = appointmentwidget.AppointmentWidget("1000", "1200", self)
        self.book.setDentist(1)
        self.book.setStartTime(1015)
        self.book.setEndTime(1145)
        for appoint in (
        (1, 1030, 1045, 'MCDONALD I', 6155L, 'EXAM', '', '', '', 1, 73, 0,
        0, datetime.datetime.now())

        ,(1, 1115, 1130, 'EMERGENCY', 0L, '', '', '', '', -128, 0, 0,
        0, datetime.datetime.now())):
            self.book.setAppointment(appoint)

        self.OVbook = AppointmentOverviewWidget("1000", "1200", 15, 2, self)

        d1 = appointments.DentistDay(1)
        d1.start=1015
        d1.end=1145
        d1.memo="hello"

        d2 = appointments.DentistDay(4)
        d2.start=1015
        d2.end=1145

        self.OVbook.dents=[d1,d2]
        self.OVbook.clear()
        self.OVbook.init_dicts()

        for d in (d1,d2):
            self.OVbook.setStartTime(d)
            self.OVbook.setEndTime(d)
            self.OVbook.setMemo(d)
            self.OVbook.setFlags(d)

        slot = appointments.FreeSlot(datetime.datetime(2009,2,2,10,45),
            1,20)
        slot2 = appointments.FreeSlot(datetime.datetime(2009,2,2,11,05),
            4,60)

        self.OVbook.addSlot(slot)
        self.OVbook.addSlot(slot2)

        appt = appointments.WeekViewAppointment()
        appt.mpm = 10*60+30
        appt.length = 15
        appt.dent = 1
        self.OVbook.appts[1] = (appt,)

        emerg = appointments.WeekViewAppointment()
        emerg.mpm = 11*60+15
        emerg.length = 15
        emerg.reason = "emergency"
        self.OVbook.eTimes[1] = (emerg,)
        self.OVbook.setMinimumWidth(200)

        self.tw = QtGui.QTabWidget(self)
        self.tw.addTab(self.book, "day")
        self.tw.addTab(self.OVbook, "week")

        layout.addWidget(self.appt_listView,0,0)
        layout.addWidget(self.blockView,2,0)

        layout.addWidget(self.tw,0,1,3,1)
        #self.tw.setCurrentIndex(1)

        self.model.appointment_selected.connect(slot_catcher)



if __name__ == "__main__":

    from openmolar.qt4gui.customwidgets import appointmentwidget
    from openmolar.qt4gui.customwidgets.appointment_overviewwidget \
         import AppointmentOverviewWidget

    from openmolar.dbtools import appointments
    from openmolar.settings import localsettings
    localsettings.initiate()

    def slot_catcher(arg):
        print arg

    class duckPt(object):
        def __init__(self):
            self.serialno = 11956
            self.title = "Mr"
            self.sname = "Neil"
            self.fname = "Wallace"
            self.cset = "P"

    app = QtGui.QApplication([])
    dl = _DragTestDialog()
    dl.exec_()

