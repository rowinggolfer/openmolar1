import datetime
import cPickle
import pickle
import sys

from PyQt4 import QtGui, QtCore
from openmolar.dbtools import appointments
from openmolar.settings import localsettings


class clinicianSelectModel(QtCore.QAbstractListModel):
    def __init__(self, om_gui):
        super(clinicianSelectModel, self).__init__(om_gui)

        self.options_list = [_("Selected Book(s)"), _("Relevant Books"),
        _("Available Dentists"), _("Available Hygenists"),
        _("Available Clinicians"), _("Everyone"), _("Manual Selection")]

        self.om_gui = om_gui
        #if localsettings.activehygs == []:
        #    self.options_list.remove(_("Available Hygenists"))

        self.manual_index = 6 #used if manual is called by another widget

    def rowCount(self, parent = QtCore.QModelIndex()):
        return len(self.options_list)

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        if role == QtCore.Qt.DisplayRole:
            option = self.options_list[index.row()]
            return QtCore.QVariant(option)
        return QtCore.QVariant()

    def clinician_list(self, row, date):
        if row == 0:
            chkset = self.om_gui.apt_drag_model.selectedClinicians
            return appointments.getWorkingDents(date, chkset,
                include_non_working = True)
        if row == 1:
            chkset = self.om_gui.apt_drag_model.involvedClinicians
            return appointments.getWorkingDents(date, chkset,
                include_non_working = True)
        elif row == 2:
            chkset = localsettings.activedent_ixs
            return appointments.getWorkingDents(date, chkset,
                include_non_working=False)
        elif row == 3:
            chkset = localsettings.activehyg_ixs
            return appointments.getWorkingDents(date, chkset,
                include_non_working=False)
        elif row == 4:
            return appointments.getWorkingDents(date,
                include_non_working=False)
        elif row == 5:
            return appointments.getWorkingDents(date)
        elif row == 6:
            return False

class simple_model(QtCore.QAbstractListModel):
    def __init__(self, parent=None):
        super(simple_model, self).__init__(parent)
        self.unscheduledList = []
        self.scheduledList = []
        self.list = []
        self.min_slot_length = 0
        self.setSupportedDragActions(QtCore.Qt.MoveAction)
        self.selection_model = QtGui.QItemSelectionModel(self)
        self.currentAppt = None
        self.selectedAppts = []
        self.normal_icon = QtGui.QIcon()
        self.normal_icon.addPixmap(QtGui.QPixmap(":/schedule.png"),
                QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.selected_icon = QtGui.QIcon()
        self.selected_icon.addPixmap(
            QtGui.QPixmap(":/icons/schedule_active.png"))

    def clear(self):
        self.unscheduledList = []
        self.scheduledList = []
        self.list = []
        self.min_slot_length = 0
        self.reset()

    @property
    def involvedClinicians(self):
        '''
        returns a set containing all clinicians referred to by the lists
        within
        '''
        retarg = set()
        for app in self.list:
            retarg.add(app.dent)
        return tuple(retarg)

    @property
    def selectedClinicians(self):
        '''
        returns a set containing all clinicians whose appointments have been
        highlighted
        '''
        retarg = set()
        for index in self.selection_model.selectedRows():
            app = self.list[index.row()]
            retarg.add(app.dent)
        return tuple(retarg)

    def setAppointments(self, appts, selectedAppt):
        '''
        add an appointments, and highlight the selectedAppt (which is the 
        highlighted one in the pt diary
        '''
        self.unscheduledList = []
        self.scheduledList = []
        self.list = []

        currentClinicians = self.involvedClinicians
        changedClinicians = True

        for appt in appts:
            if appt.past:
                pass
            elif appt.unscheduled:
                self.unscheduledList.append(appt)
            else:
                self.scheduledList.append(appt)

            if not appt.past and not (appt.dent in currentClinicians):
                changedClinicians = True

        self.list = self.scheduledList + self.unscheduledList
        
        if changedClinicians:
            self.emit(QtCore.SIGNAL("clinicianListChanged"))
        
        self.reset()

        for appt in self.selectedAppts:
            self.setcurrentAppt(appt)            

        if selectedAppt in appts:
            self.setcurrentAppt(selectedAppt)
        else:
            self.setcurrentAppt(None)        
        
    def rowCount(self, parent = QtCore.QModelIndex()):
        return len(self.list)

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        app = self.list[index.row()]
        if role == QtCore.Qt.DisplayRole:
            if app.flag == -128:
                info = "%s (%s)"% (app.name, app.length)
            elif app.unscheduled:
                info = "%s %s - %s"% (app.length,
                    app.trt1, app.dent_inits)
            else:
                info = "%s %s with %s"% (app.readableDate,
                    app.readableTime, app.dent_inits)
            return QtCore.QVariant(info)
        elif role == QtCore.Qt.ForegroundRole:
            if app.unscheduled:
                return QtCore.QVariant(QtGui.QBrush(QtGui.QColor("red")))
        elif role == QtCore.Qt.DecorationRole:
            #if app in self.selectedAppts: #
            if app.unscheduled:
                if app == self.currentAppt:
                    return QtCore.QVariant(self.selected_icon)
                return QtCore.QVariant(self.normal_icon)
        elif role == QtCore.Qt.UserRole:  #return the whole python object
            return app
        return QtCore.QVariant()

    def setSelectedIndexes(self, indexes, selected):
        self.min_slot_length = 0
        self.currentAppt = None
        self.selectedAppts = []
        for index in indexes:
            appt = self.data(index, QtCore.Qt.UserRole)
            self.selectedAppts.append(appt)
        
        if selected in indexes:
            self.currentAppt = self.data(selected, QtCore.Qt.UserRole)
            self.min_slot_length = self.currentAppt.length
        elif self.selectedAppts != []:
            self.currentAppt = self.selectedAppts[0]
            self.min_slot_length = self.currentAppt.length
        
        self.emit(QtCore.SIGNAL("selectedAppointment"), self.currentAppt)

    def setcurrentAppt(self, appt):
        self.currentAppt = appt
        if appt == None:
            self.selection_model.clear()
            self.min_slot_length = 0
        else:
            try:
                index = self.index(self.list.index(appt))
                self.min_slot_length = appt.length
                self.selection_model.select(index,
                    QtGui.QItemSelectionModel.Select)
            except ValueError:
                pass


class blockModel(simple_model):
    '''
    customise the above model just for blocks
    '''
    def __init__(self, parent=None):
        super(blockModel, self).__init__(parent)
        self.list = []
        for val, length in (
        (_("Lunch"), 60),
        (_("Lunch"), 30),
        (_("staff meeting"), 10),
        (_("emergency"), 15),
        (_("emergency"), 20),
        (_("emergency"), 30),
        (_("Out of Office"), 30)):
            block = appointments.appt_class()
            block.name = val
            block.unscheduled = True
            block.length = length
            block.flag = -128
            self.list.append(block)

    def reset(self):
        pass

class draggableList(QtGui.QListView):
    '''
    a listView whose items can be moved
    '''
    def __init__(self, multiSelect, parent=None):
        super(draggableList, self).__init__(parent)
        self.setDragEnabled(True)
        if multiSelect:
            self.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.pixels_per_min = 2
        self.setMinimumHeight(150)

    def setScaling(self, height_per_minute):
        '''
        make the list aware of the scaling of the widget available for drops
        this will differ depending on whether a day or week view is visible
        a 20 minutes slot will be x pixels high...
        '''
        self.pixels_per_min = height_per_minute

    def startDrag(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return

        ## selected is the relevant person object
        selectedApp = self.model().data(index, QtCore.Qt.UserRole)

        if not selectedApp.unscheduled:
            event.ignore()
            return
        if index not in self.selectedIndexes():
            self.setCurrentIndex(index)

        ## convert to  a bytestream
        bstream = cPickle.dumps(selectedApp)
        mimeData = QtCore.QMimeData()
        mimeData.setData("application/x-appointment", bstream)
        drag = QtGui.QDrag(self)

        drag.setMimeData(mimeData)
        drag.setDragCursor(QtGui.QPixmap(), QtCore.Qt.MoveAction)

        #pmap = QtGui.QPixmap(50 , selectedApp.length * self.pixels_per_min)
        #pmap.fill(QtGui.QColor(127,0,0))
        #drag.setHotSpot(QtCore.QPoint(pmap.width()/2, pmap.height()/2)

        pixmap = QtGui.QPixmap()
        pixmap = pixmap.grabWidget(self, self.rectForIndex(index))
        drag.setPixmap(pixmap)
        drag.setHotSpot(QtCore.QPoint(-10,0))

        drag.start(QtCore.Qt.CopyAction)

    def mouseMoveEvent(self, event):
        self.startDrag(event)

    def mousePressEvent(self, event):
        ##set this to ignore, and use mouse Release instead
        event.ignore()

    def mouseReleaseEvent(self, event):
        event = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonPress, event.pos(),
            event.button(), event.buttons(), QtCore.Qt.NoModifier)
        QtGui.QListView.mousePressEvent(self, event)

    def selectionChanged (self, selectedRange, deselected):
        '''
        the user has selected an appointment (or range of appointments!)
        from the list

        currently, the model is a single selection
        '''
        if selectedRange.count():
            selected = selectedRange.indexes()[0]
        else:
            selected = None
        rows = self.selectionModel().selectedRows()
        self.model().setSelectedIndexes(rows, selected)

        self.doItemsLayout()

if __name__ == "__main__":
    '''
    the try catch here is to ensure that the app exits cleanly no matter what
    makes life better for SPE
    '''
    from openmolar.qt4gui.customwidgets import appointmentwidget
    from openmolar.qt4gui.customwidgets import appointment_overviewwidget

    from openmolar.dbtools import appointments
    from openmolar.settings import localsettings
    localsettings.initiate()

    def slot_catcher(arg):
        print arg

    class duckPt(object):
        def __init__(self):
            self.serialno = 707
            self.title = "Mr"
            self.sname = "Neil"
            self.fname = "Wallace"
            self.cset = "P"

    class testDialog(QtGui.QDialog):
        def __init__(self, parent=None):
            super(testDialog, self).__init__(parent)
            self.setWindowTitle("Drag Drop Test")
            self.pt = duckPt()

            layout = QtGui.QGridLayout(self)

            self.model = simple_model()

            appts = appointments.get_pts_appts(duckPt())

            self.model.setAppointments(appts, appts[2])

            self.daylistView = draggableList(True)
            self.daylistView.setModel(self.model)
            self.daylistView.setSelectionModel(self.model.selection_model)

            self.weeklistView = draggableList(True)
            self.weeklistView.setModel(self.model)
            self.weeklistView.setSelectionModel(
                self.daylistView.selectionModel())

            self.block_model = blockModel()
            self.blockView = draggableList(False)
            self.blockView.setModel(self.block_model)

            self.book = appointmentwidget.appointmentWidget(self, "1000",
            "1200")
            self.book.setDentist(1)
            self.book.setStartTime(1015)
            self.book.setEndTime(1145)
            for appoint in (
            (1, 1030, 1045, 'MCDONALD I', 6155L, 'EXAM', '', '', '', 1, 73, 0,
            0, datetime.datetime.now())

            ,(1, 1115, 1130, 'EMERGENCY', 0L, '', '', '', '', -128, 0, 0,
            0, datetime.datetime.now())):
                self.book.setAppointment(appoint)

            self.OVbook = appointment_overviewwidget.bookWidget(1,
            "1000", "1200", 15, 2, self)

            d1 = appointments.dentistDay(1)
            d1.start=1015
            d1.end=1145
            d1.memo="hello"

            d2 = appointments.dentistDay(4)
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

            slot = appointments.freeSlot(datetime.datetime(2009,2,2,10,45),
                1,20)
            slot2 = appointments.freeSlot(datetime.datetime(2009,2,2,11,05),
                4,60)

            self.OVbook.addSlot(slot)
            self.OVbook.addSlot(slot2)

            appt = appointments.aowAppt()
            appt.mpm = 10*60+30
            appt.length = 15
            appt.dent = 1
            self.OVbook.appts[1] = (appt,)

            emerg = appointments.aowAppt()
            emerg.mpm = 11*60+15
            emerg.length = 15
            emerg.reason = "emergency"
            self.OVbook.eTimes[1] = (emerg,)
            self.OVbook.setMinimumWidth(200)

            self.tw = QtGui.QTabWidget(self)
            self.tw.addTab(self.book, "day")
            self.tw.addTab(self.OVbook, "week")

            layout.addWidget(self.daylistView,0,0)
            layout.addWidget(self.weeklistView,1,0)
            layout.addWidget(self.blockView,2,0)

            layout.addWidget(self.tw,0,1,3,1)
            #self.tw.setCurrentIndex(1)

            self.connect(self.model, QtCore.SIGNAL("selectedAppointment"),
                slot_catcher)

            self.connect(self.OVbook, QtCore.SIGNAL("redrawn"),
                    self.weeklistView.setScaling)
            self.connect(self.book, QtCore.SIGNAL("redrawn"),
                    self.daylistView.setScaling)

    try:
        app = QtGui.QApplication([])
        dl = testDialog()
        dl.exec_()
    except Exception, e:
        print e
    sys.exit(app.closeAllWindows())
