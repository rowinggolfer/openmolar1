import datetime
import cPickle
import pickle
import sys

from PyQt4 import QtGui, QtCore
from openmolar.dbtools.appointments import appt_class

class simple_model(QtCore.QAbstractListModel):
    def __init__(self, parent=None):
        super(simple_model, self).__init__(parent)
        self.unscheduledList = []
        self.scheduledList = []
        self.list = []
        self.setSupportedDragActions(QtCore.Qt.MoveAction)

    def clear(self):
        self.unscheduledList = []
        self.scheduledList = []
        self.list = []
        self.reset()

    def addAppointment(self, app):
        '''
        add an appointment to this list - arg is of type dragAppointment
        '''
        if app.unscheduled:
            self.unscheduledList.append(app)
        else:
            self.scheduledList.append(app)            
        self.list = self.scheduledList + self.unscheduledList
                
        self.reset()

    def rowCount(self, parent = QtCore.QModelIndex()):
        return len(self.list)

    def data(self, index, role):
        app = self.list[index.row()]
        if role == QtCore.Qt.DisplayRole:
            if app.flag == -128:
                info = "%s (%s %s)"% (app.name, app.length, _("mins"))
            elif app.unscheduled:
                info = "%s %s %s %s %s"% (app.length, _("mins"), 
                    app.trt1, _("with"), app.dent_inits)
            else:
                info = "%s %s with %s"% (app.readableDate, 
                    app.readableTime, app.dent_inits)
            return QtCore.QVariant(info)
        elif role == QtCore.Qt.ForegroundRole:
            if app.unscheduled:
                return QtCore.QVariant(QtGui.QBrush(QtGui.QColor("red")))
        elif role == QtCore.Qt.UserRole:  #return the whole python object
            return app
        return QtCore.QVariant()

    def removeRow(self, position):
        self.list = self.list[:position] + self.list[position+1:]
        self.reset()

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
        (_("Emergency"), 15),
        (_("Emergency"), 20),
        (_("Emergency"), 30),        
        (_("Out of Office"), 30)):
            block = appt_class()
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
    def __init__(self, parent=None):
        super(draggableList, self).__init__(parent)
        self.setDragEnabled(True)
        self.dropwidth = self.width()
        self.pixels_per_min = 2
    
    def setScaling(self, width, height_per_minute):
        '''
        make the list aware of the scaling of the widget available for drops
        this will differ depending on whether a day or week view is visible
        a 20 minutes slot will be x pixels high...
        '''
        self.dropwidth = width
        self.pixels_per_min = height_per_minute

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-appointment"):
            event.setDropAction(QtCore.Qt.QMoveAction)
            event.accept()
        else:
            event.ignore()

    def startDrag(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return

        ## selected is the relevant person object
        selectedApp = self.model().data(index,QtCore.Qt.UserRole)

        if not selectedApp.unscheduled:
            return
        
        ## convert to  a bytestream
        bstream = cPickle.dumps(selectedApp)
        mimeData = QtCore.QMimeData()
        mimeData.setData("application/x-appointment", bstream)
        drag = QtGui.QDrag(self)

        drag.setMimeData(mimeData)
        drag.setDragCursor(QtGui.QPixmap(), QtCore.Qt.MoveAction)

        #pmap = QtGui.QPixmap(100,
        #    selectedApp.length * self.pixels_per_min)
        #pmap.fill(QtGui.QColor(127,0,0))
        #drag.setHotSpot(QtCore.QPoint(pmap.width()/2, pmap.height()/2))
        #drag.setPixmap(pmap)
        
        if selectedApp.serialno !=0:
            result = drag.start(QtCore.Qt.MoveAction)
            if result: # == QtCore.Qt.MoveAction:
                self.model().removeRow(index.row())
        else:
            result = drag.start(QtCore.Qt.CopyAction)
            if result:
                pass
                        
    def mouseMoveEvent(self, event):
        self.startDrag(event)

    def selectionChanged (self, selectedRange, deselected):
        '''
        the user has selected an appointment (or range of appointments!)
        from the list
        
        currently, the model is a single selection
        '''
        selected = selectedRange.first().topLeft()
        selectedApp = self.model().data(selected,QtCore.Qt.UserRole)
        self.emit(QtCore.SIGNAL("appointmentSelected"), selectedApp)

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
    
    class duckPt(object):
        def __init__(self):
            self.serialno = 1
            self.sname = "Neil"
            self.fname = "Wallace"
            self.cset = "P"

    class testDialog(QtGui.QDialog):
        def __init__(self, parent=None):
            super(testDialog, self).__init__(parent)
            self.setWindowTitle("Drag Drop Test")
            self.pt = duckPt()
            
            layout = QtGui.QHBoxLayout(self)

            self.model = simple_model()
            appts = appointments.get_pts_appts(duckPt())
            for appt in appts:
                if appt.unscheduled:
                    self.model.addAppointment(appt)

            self.listView = draggableList()
            self.listView.setModel(self.model)

            self.book = appointmentwidget.appointmentWidget(self, "1000",
            "1200")
            self.book.setDentist(1)
            self.book.setStartTime(1015)
            self.book.setEndTime(1145)
            for appoint in (
            (1, 1030, 1045, 'MCDONALD I', 6155L, 'EXAM', '', '', '', 1, 73, 0, 0)
            ,(1, 1115, 1130, 'EMERGENCY', 0L, '', '', '', '', -128, 0, 0, 0)):
                self.book.setAppointment(appoint)

            self.OVbook = appointment_overviewwidget.bookWidget(1,
            "1000", "1200", 15, 2, self)
            d1 = appointments.dentistDay(1)

            d1.start=1015
            d1.end=1145
            d1.memo="hello"

            self.OVbook.dents=[d1,]
            self.OVbook.clear()
            self.OVbook.init_dicts()

            self.OVbook.setStartTime(d1)
            self.OVbook.setEndTime(d1)
            self.OVbook.setMemo(d1)
            self.OVbook.setFlags(d1)

            slot = appointments.freeSlot(datetime.datetime(2009,2,2,10,45),1,20)
            slot2 = appointments.freeSlot(datetime.datetime(2009,2,2,11,05),1,10)
            self.OVbook.addSlot(slot)
            self.OVbook.addSlot(slot2)
            
            self.OVbook.appts[1] = ((2,1030,15),)
            self.OVbook.eTimes[1] = ((1115, 15),)
            self.OVbook.setMinimumWidth(200)

            self.tw = QtGui.QTabWidget(self)
            self.tw.addTab(self.book, "day")
            self.tw.addTab(self.OVbook, "week")

            layout.addWidget(self.listView)
            layout.addWidget(self.tw)

            #self.connect(self.tw, QtCore.SIGNAL("currentChanged (int)"),
            #    self.tabNav)

            self.connect(self.OVbook, QtCore.SIGNAL("redrawn"),
                    self.listView.setScaling)
            self.connect(self.book, QtCore.SIGNAL("redrawn"),
                    self.listView.setScaling)

        #def tabNav(self, index):
        #    widg = self.tw.currentWidget()
        #    self.listView.setScaling(widg.dragWidth, widg.dragScale)

    try:
        app = QtGui.QApplication([])
        dl = testDialog()
        dl.exec_()
    except Exception, e:
        print e
    sys.exit(app.closeAllWindows())
