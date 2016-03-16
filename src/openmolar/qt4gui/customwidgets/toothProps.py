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

from gettext import gettext as _
import logging
import re

from PyQt5 import QtCore, QtGui, QtWidgets

from openmolar.settings import localsettings
from openmolar.settings import allowed
from openmolar.qt4gui.compiled_uis import Ui_toothProps
from openmolar.qt4gui import colours
from openmolar.qt4gui.dialogs.crown_choice_dialog import CrownChoiceDialog
from openmolar.qt4gui.dialogs.post_choice_dialog import PostChoiceDialog
from openmolar.qt4gui.dialogs.implant_choice_dialog import ImplantChoiceDialog
from openmolar.qt4gui.dialogs.chart_tx_choice_dialog import ChartTxChoiceDialog
from openmolar.qt4gui.dialogs.bridge_dialog import BridgeDialog

from openmolar.qt4gui.dialogs import toothprop_fulledit

LOGGER = logging.getLogger("openmolar")


class chartLineEdit(QtWidgets.QLineEdit):

    '''
    A custom line edit that accepts only BLOCK LETTERS
    and is self aware when verification is needed
    override the keypress event for up and down arrow keys.
    '''
    changed_properties_signal = QtCore.pyqtSignal(object)
    deleted_comments_signal = QtCore.pyqtSignal()
    nav_key_pressed_signal = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        QtWidgets.QLineEdit.__init__(self, parent)
        self.om_gui = parent
        self.originalPropList = []

    def unsavedChanges(self):
        '''
        checks for unsaved changes
        '''
        result = not (self.originalPropList == self.propListFromText())
        return result

    def deleteAll(self):
        '''
        deletes all props
        '''
        self.setText("")
        self.finishedEdit()

    def deleteProp(self, prop):
        '''
        deletes all props
        '''
        new_props = []
        found = False
        for ex_prop in self.propListFromText():
            if not found and ex_prop.upper() == prop.upper():
                found = True
            else:
                new_props.append(ex_prop)
        self.updateFromPropList(new_props)

    def finishedEdit(self):
        '''
        we have finished editing the text.. let the main gui know by
        means of a signal
        '''
        props = self.text()
        if props != "" or (props == "" and self.originalPropList != []):
            if not re.match("..* $", props):
                if props != "":
                    props = props + " "
            self.changed_properties_signal.emit(props)

    def additional(self, checkedAlready=False):
        '''
        we have finished editing, and moving on
        '''
        if checkedAlready or self.verifyProps():
            self.updateFromPropList(self.propListFromText())
            self.om_gui.tooth.clear()
            self.om_gui.tooth.update()
            self.finishedEdit()

    def propListFromText(self):
        '''
        returns the current property list
        '''
        text = self.text()
        propList = text.strip(" ").split(" ")
        return propList

    def updateFromPropList(self, propList):
        text = ""
        for prop in propList:
            if prop not in ("", " "):
                text += "%s " % prop
        self.setKnownProps(text)
        # not sure these are needed??
        self.om_gui.tooth.clear()
        self.om_gui.tooth.update()
        self.finishedEdit()

    def setKnownProps(self, arg):
        '''
        put a string of props into the text, and set the known list of
        properties
        '''
        self.setText(arg)
        self.originalPropList = self.propListFromText()

    def verifyProps(self):
        '''
        verify that the current text is valid
        '''
        snapshotPropList = self.propListFromText()
        if snapshotPropList == self.originalPropList:
            return True
        for prop in self.originalPropList:
            if prop not in snapshotPropList:
                self.originalPropList.remove(prop)
        verified = True
        for prop in snapshotPropList:
            if (self.om_gui.selectedChart == "st" and
               not self.propAllowed(prop)):
                verified = False
            else:
                self.originalPropList.append(prop)
        return verified

    def deleteComments(self):
        snapshotPropList = self.propListFromText()
        deleted = False
        for prop in snapshotPropList:
            if prop[:1] == "!":
                snapshotPropList.remove(prop)
                deleted = True
        if deleted:
            self.updateFromPropList(snapshotPropList)
            self.deleted_comments_signal.emit()

    def addItem(self, item):
        if item not in ("", " "):
            snapshotPropList = self.propListFromText()
            snapshotPropList.append(item)
            self.updateFromPropList(snapshotPropList)

    def removeItem(self, item):
        if item == "":
            return
        snapshotPropList = self.propListFromText()
        snapshotPropList.remove(item)
        self.updateFromPropList(snapshotPropList)

    def removeEndItem(self):
        '''
        user has pressed the delete button
        remove the last item
        '''
        snapshotPropList = self.propListFromText()
        self.updateFromPropList(snapshotPropList[:-1])

    def propAllowed(self, prop):
        '''
        check to see if the user has entered garbage
        '''
        LOGGER.debug("checking propAllowed '%s' origs ='%s'", prop,
                     self.originalPropList)
        if prop == "":
            return True
        if prop[:1] == "!":  # comment
            return True
        if prop in self.originalPropList:
            return True

        if self.om_gui.tooth.isBacktooth:
            allowed_prop = prop in allowed.backToothCodes
        else:
            allowed_prop = prop in allowed.frontToothCodes
        if not self.om_gui.is_Static:
            if prop in allowed.treatment_only:
                allowed_prop = True
        if not allowed_prop:
            message = '"%s" %s <br /> %s?' % (
                prop, _("is not recognised"),
                _("do you want to accept anyway"))
            allowed_prop = QtWidgets.QMessageBox.question(
                self, _("Confirm"), message,
                QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes,
                QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes
        if allowed_prop:
            LOGGER.debug("toothProps - accepting new entry '%s'" % prop)
        return allowed_prop

    def specialKeyPressed(self, arg):
        '''
        handles the events when a user hits space, up, down or return
        '''
        if arg in ("up", "down"):
            self.nav_key_pressed_signal.emit(arg)
        else:
            self.additional()

    def keyPressEvent(self, event):
        '''
        overrides QWidget's keypressEvent.
        Catch special keys, and disable lower case
        '''
        if event.key() == QtCore.Qt.Key_Up:
            self.specialKeyPressed("up")
            return
        if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Down):
            self.specialKeyPressed("down")
            return
        if event.text() == "!" and not self.om_gui.is_Static:
            # don't allow comments if not in static:
            return

        if event.key() == QtCore.Qt.Key_Space:
            self.specialKeyPressed("space")
        elif 65 <= event.key() <= 90:
            event = QtGui.QKeyEvent(
                event.type(),
                event.key(),
                event.modifiers(),
                event.text().upper()
            )

        QtWidgets.QLineEdit.keyPressEvent(self, event)


class ToothPropertyEditingWidget(QtWidgets.QWidget, Ui_toothProps.Ui_Form):
    static_chosen = QtCore.pyqtSignal(object)
    next_tooth_signal = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.om_gui = parent
        self.setupUi(self)
        hlayout = QtWidgets.QHBoxLayout(self.editframe)
        hlayout.setContentsMargins(0, 0, 0, 0)
        self.lineEdit = chartLineEdit(self)
        self.lineEdit.setMaxLength(34)
        # as defined in the sql tables for a static entry -
        # may exceed the plan stuff.... but I will validate that anyway.

        hlayout.addWidget(self.lineEdit)
        self.tooth = Tooth()
        self.toothlayout = QtWidgets.QHBoxLayout(self.frame)
        self.toothlayout.setContentsMargins(2, 2, 2, 2)
        self.toothlayout.setSpacing(2)
        self.toothlayout.addWidget(self.tooth)

        icon = QtGui.QIcon(":/pin.png")
        pin_button = QtWidgets.QPushButton(icon, "")
        pin_button.setMaximumWidth(30)
        pin_button.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        pin_button.setToolTip(_("Toggle Pin Retention for current Filling"))
        self.toothlayout.addWidget(pin_button)

        self.am_pushButton.setStyleSheet(
            "background-color: %s" % colours.AMALGAM_)
        self.co_pushButton.setStyleSheet(
            "background-color: %s" % colours.COMP_)
        self.gl_pushButton.setStyleSheet(
            "background-color: %s" % colours.GI_)
        self.gold_pushButton.setStyleSheet(
            "background-color: %s" % colours.GOLD_)
        self.porc_pushButton.setStyleSheet(
            "background-color: %s" % colours.PORC_)

        self.is_Static = False
        self.selectedChart = ""
        self.selectedTooth = ""
        self.comboboxes = []
        self.crown_but = QtWidgets.QPushButton(_("Crowns"))
        self.post_but = QtWidgets.QPushButton(_("Posts"))
        self.bridge_but = QtWidgets.QPushButton(_("Bridges"))
        self.implant_but = QtWidgets.QPushButton(_("Implants"))
        self.fs_but = QtWidgets.QPushButton(_("Fissure Sealants"))
        self.endo_but = QtWidgets.QPushButton(_("Endodontics"))
        self.surgical_but = QtWidgets.QPushButton(_("Surgical Tx"))

        frame = QtWidgets.QFrame()
        vlayout = QtWidgets.QVBoxLayout(frame)
        # vlayout.setMargin(0)
        vlayout.addWidget(self.fs_but)
        vlayout.addWidget(self.endo_but)
        vlayout.addWidget(self.crown_but)
        vlayout.addWidget(self.post_but)
        vlayout.addWidget(self.bridge_but)
        vlayout.addWidget(self.surgical_but)
        vlayout.addWidget(self.implant_but)
        vlayout.addStretch(100)

        self.cb_scrollArea.setWidget(frame)
        self.cb_scrollArea.setWidgetResizable(True)

        self.signals()
        pin_button.clicked.connect(self.toggle_pin)

    def sizeHint(self):
        return QtCore.QSize(120, 500)

    def setTooth(self, selectedTooth, selectedChart):
        '''
        make the widget aware of exactly what it is editing
        selectedTooth will be 'ur8' etc..
        selectedChart will be 'st' or 'pl' or 'cmp'
        '''
        self.setSelectedChart(selectedChart)

        self.selectedTooth = selectedTooth

        self.tooth.setBacktooth(int(selectedTooth[2]) > 3)
        self.tooth.setRightSide(selectedTooth[1] == "r")
        self.tooth.setUpper(selectedTooth[0] == "u")

        self.tooth.clear()
        self.tooth.update()

        # ALLOWS for deciduous teeth
        self.tooth_label.setText(
            self.om_gui.pt.chartgrid[selectedTooth].upper())

        if selectedChart == "st":
            self.isStatic(True)
            props = self.om_gui.pt.__dict__["%sst" % selectedTooth]
        else:
            self.isStatic(False)
            props = self.om_gui.pt.treatment_course.__dict__[
                "%s%s" % (selectedTooth, selectedChart)]

        self.setExistingProps(props)

    def setSelectedChart(self, arg):
        '''
        make the widget aware which chart it is linked to
        '''
        self.selectedChart = arg
        self.isStatic(arg == "st")
        self.static_chosen.emit(arg == "st")

    def isStatic(self, arg):
        '''
        if the editing is of the static chart,
        then different buttons are enabled
        '''
        self.is_Static = arg
        self.comments_comboBox.setEnabled(arg)
        self.ex_pushButton.setEnabled(not arg)

    def comments(self, arg):
        '''
        comments combobox has been nav'd
        '''
        if _("ADD COMMENTS") in arg:
            return
        elif arg == _("DELETE ALL COMMENTS"):
            self.lineEdit.deleteComments()
        else:
            newComment = "!%s" % arg.replace(" ", "_")
            self.lineEdit.addItem(newComment)

        self.comments_comboBox.setCurrentIndex(0)

    def fulledit(self):
        '''
        user has clicked the edit button
        allow the user to edit the full contents of a tootget\ h
        '''
        Dialog = QtWidgets.QDialog(self)
        lineEdit = chartLineEdit()
        if self.selectedChart == "st":
            lineEdit.setMaxLength(34)
        lineEdit.setText(self.lineEdit.text())

        dl = toothprop_fulledit.editor(self.selectedTooth, self.selectedChart,
                                       lineEdit, Dialog)

        if dl.exec_():
            self.lineEdit.setText(dl.result)
            self.lineEdit.additional()
        else:
            self.lineEdit.updateFromPropList(self.lineEdit.originalPropList)

    def setExistingProps(self, arg):
        self.lineEdit.setKnownProps(arg)

    def updateSurfaces(self):
        existing = self.lineEdit.text()
        if " " in existing:  # we have an existing property in the tooth
            colonPos = existing.rindex(" ")
            keep = existing[:colonPos + 1]
            currentFill = existing[colonPos:]
        else:  # we don't
            keep = ""
            currentFill = existing
        if "," in currentFill:  # we have a material
            split = currentFill.split(",")
            mat = "," + split[1]
            currentFill = self.tooth.filledSurfaces + mat
        elif "/" in currentFill:  # we have a lab item
            split = currentFill.split("/")
            mat = split[0] + "/"
            currentFill = mat + self.tooth.filledSurfaces
        else:  # virgin tooth
            currentFill = self.tooth.filledSurfaces

        if currentFill.startswith(",") or currentFill.endswith("/ "):
            currentFill = ""

        self.lineEdit.setText(keep + currentFill)

    def changeFillColour(self, arg):
        self.tooth.fillcolour = arg
        self.tooth.update()

    def plasticMaterial(self, arg):
        existing = self.lineEdit.text()
        if " " in existing:
            colonPos = existing.rindex(" ")
            keep = existing[:colonPos + 1]
            currentFill = existing[colonPos + 1:]
        else:
            keep = ""
            currentFill = existing
        pinned = ",PR" in currentFill
        if pinned:
            currentFill = currentFill.replace(",PR", "")
        if currentFill.strip(" ") == "":
            return
        if "/" in currentFill:  # already has a lab item
            split = currentFill.split("/")
            surfaces = split[1]
            currentFill = surfaces + "," + arg
        elif "," in currentFill:  # already a material set! replace it.
            split = currentFill.split(",")
            surfaces = split[0]
            currentFill = surfaces + "," + arg
        else:
            currentFill += "," + arg

        if pinned:
            currentFill += ",PR"

        self.lineEdit.setText(keep + currentFill)

    def toggle_pin(self):
        existing = self.lineEdit.text()
        if " " in existing:
            colonPos = existing.rindex(" ")
            keep = existing[:colonPos + 1]
            current = existing[colonPos + 1:]
        else:
            keep = ""
            current = existing
        if current.strip(" ") == "":
            return
        if ",PR" in current:
            current = current.replace(",PR", "")
        else:
            current += ",PR"
        self.lineEdit.setText(keep + current)

    def labMaterial(self, arg):
        existing = self.lineEdit.text()
        if " " in existing:
            colonPos = existing.rindex(" ")
            keep = existing[:colonPos + 1]
            currentFill = existing[colonPos + 1:]
        else:
            keep = ""
            currentFill = existing
        if currentFill.strip(" ") == "":
            return
        pinned = ",PR" in currentFill
        if pinned:
            currentFill = currentFill.replace(",PR", "")

        if "," in currentFill:  # already a material set! replace it.
            split = currentFill.split(",")
            surfaces = split[0]
            currentFill = arg + "/" + surfaces
        elif "/" in currentFill:  # already has a lab item
            split = currentFill.split("/")
            surfaces = split[1]
            currentFill = arg + "/" + surfaces
        else:
            currentFill = arg + "/" + currentFill

        if pinned:
            currentFill += ",PR"

        self.lineEdit.setText(keep + currentFill)

    def am(self):
        self.changeFillColour(colours.AMALGAM)
        self.plasticMaterial("AM")

    def co(self):
        self.changeFillColour(colours.COMP)
        self.plasticMaterial("CO")

    def gl(self):
        self.changeFillColour(colours.GI)
        self.plasticMaterial("GL")

    def go(self):
        self.changeFillColour(colours.GOLD)
        self.labMaterial("GI")

    def pi(self):
        self.changeFillColour(colours.PORC)
        self.labMaterial("PI")

    def keyNav(self, arg):
        if arg == "up":
            self.prevTooth()
        elif arg == "down":
            self.nextTooth()

    def leftTooth(self):
        if self.tooth.isUpper:
            self.prevTooth()
        else:
            self.nextTooth()

    def rightTooth(self):
        if not self.tooth.isUpper:
            self.prevTooth()
        else:
            self.nextTooth()

    def prevTooth(self):
        if self.lineEdit.verifyProps():
            self.lineEdit.finishedEdit()
            self.next_tooth_signal.emit("up")

    def nextTooth(self):
        if self.lineEdit.verifyProps():
            self.lineEdit.finishedEdit()
            self.next_tooth_signal.emit("down")

    def static_input(self, value):
        self.lineEdit.addItem(value)
        self.nextTooth()

    def ex(self):
        self.lineEdit.addItem("EX")
        self.nextTooth()

    def rt(self):
        self.lineEdit.addItem("RT")
        self.lineEdit.additional()

    def dressing(self):
        self.lineEdit.addItem("DR")
        self.lineEdit.additional()

    def crown(self):
        dl = CrownChoiceDialog(self.is_Static, self.om_gui)
        if dl.exec_():
            self.lineEdit.addItem(dl.chosen_shortcut)
            self.lineEdit.additional()

    def posts(self):
        dl = PostChoiceDialog(self.is_Static, self.om_gui)
        if dl.exec_():
            self.lineEdit.addItem(dl.chosen_shortcut)
            self.lineEdit.additional()

    def bridge(self):
        dl = BridgeDialog(self.om_gui)
        if dl.exec_():
            for tooth, tx in dl.chosen_treatments:
                LOGGER.debug("adding bridge unit '%s' '%s'" % (tooth, tx))
                self.setTooth(tooth, self.selectedChart)
                self.lineEdit.addItem(tx)
            self.lineEdit.additional()

    def implant_but_clicked(self):
        dl = ImplantChoiceDialog(self.is_Static, self.om_gui)
        if dl.exec_():
            self.lineEdit.addItem(dl.chosen_shortcut)
            self.nextTooth()

    def fs_but_clicked(self):
        dl = ChartTxChoiceDialog(self.is_Static, self.om_gui)
        if self.is_Static:
            dl.set_items(dl.FS_ITEMS)
        else:
            dl.add_buttons(
                self.om_gui.pt.fee_table.ui_lists["fs_buttons"],
                localsettings.FEETABLES.ui_fs_chart_buttons)
        if dl.exec_():
            self.lineEdit.addItem(dl.chosen_shortcut)
            self.lineEdit.additional()

    def endo_but_clicked(self):
        dl = ChartTxChoiceDialog(self.is_Static, self.om_gui)
        if self.is_Static:
            dl.set_items(dl.ENDO_ITEMS)
        else:
            dl.add_buttons(
                self.om_gui.pt.fee_table.ui_lists["endo_buttons"],
                localsettings.FEETABLES.ui_endo_chart_buttons)
        if dl.exec_():
            self.lineEdit.addItem(dl.chosen_shortcut)
            self.lineEdit.additional()

    def surgical_but_clicked(self):
        dl = ChartTxChoiceDialog(self.is_Static, self.om_gui)
        if self.is_Static:
            dl.set_items(dl.SURGICAL_ITEMS)
        else:
            dl.add_buttons(
                self.om_gui.pt.fee_table.ui_lists["surgical_buttons"],
                localsettings.FEETABLES.ui_surgical_chart_buttons)
        if dl.exec_():
            self.lineEdit.addItem(dl.chosen_shortcut)
            self.lineEdit.additional()

    def signals(self):

        self.tooth.surfaces_changed_signal.connect(self.updateSurfaces)
        self.lineEdit.nav_key_pressed_signal.connect(self.keyNav)
        self.comments_comboBox.currentIndexChanged[str].connect(self.comments)
        self.am_pushButton.clicked.connect(self.am)
        self.co_pushButton.clicked.connect(self.co)
        self.gl_pushButton.clicked.connect(self.gl)
        self.gold_pushButton.clicked.connect(self.go)
        self.porc_pushButton.clicked.connect(self.pi)
        self.clear_pushButton.clicked.connect(self.lineEdit.removeEndItem)
        self.edit_pushButton.clicked.connect(self.fulledit)
        self.pushButton.clicked.connect(self.lineEdit.additional)
        self.rightTooth_pushButton.clicked.connect(self.rightTooth)
        self.leftTooth_pushButton.clicked.connect(self.leftTooth)
        self.ex_pushButton.clicked.connect(self.ex)
        self.rt_pushButton.clicked.connect(self.rt)
        self.dressing_pushButton.clicked.connect(self.dressing)
        self.crown_but.clicked.connect(self.crown)
        self.post_but.clicked.connect(self.posts)
        self.bridge_but.clicked.connect(self.bridge)
        self.implant_but.clicked.connect(self.implant_but_clicked)
        self.fs_but.clicked.connect(self.fs_but_clicked)
        self.endo_but.clicked.connect(self.endo_but_clicked)
        self.surgical_but.clicked.connect(self.surgical_but_clicked)


class Tooth(QtWidgets.QWidget):
    surfaces_changed_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.isBacktooth = True
        self.quadrant = 1
        self.isUpper = True
        self.isRight = True
        self.setMouseTracking(True)
        self.shapes()
        self.clear()

    def sizeHint(self):
        return self.parent().size()

    def minimumSizeHint(self):
        return QtCore.QSize(80, 80)

    def setBacktooth(self, arg):
        if self.isBacktooth != arg:
            self.isBacktooth = arg
            self.shapes()

    def setRightSide(self, arg):
        self.isRight = arg

    def setUpper(self, arg):
        self.isUpper = arg

    def clear(self):
        self.filledSurfaces = ""
        if self.isBacktooth:
            self.fillcolour = colours.AMALGAM
        else:
            self.fillcolour = colours.COMP

    def sortSurfaces(self, arg):
        '''
        sort the filling surfaces to fit with conventional notation
        eg... MOD not DOM etc..
        '''
        retarg = ""
        if "M" in arg:
            retarg += "M"
        if "D" in arg and "M" not in retarg:
            retarg += "D"
        if "O" in arg:
            retarg += "O"
        if "D" in arg and "D" not in retarg:
            retarg += "D"
        if "B" in arg:
            retarg += "B"
        if "P" in arg:
            retarg += "P"
        if "L" in arg:
            retarg += "L"
        if "I" in arg:
            retarg += "I"

        return retarg

    def setFilledSurfaces(self, arg):
        if arg in self.filledSurfaces:
            self.filledSurfaces = self.filledSurfaces.replace(arg, "")
        else:
            self.filledSurfaces += arg
        self.filledSurfaces = self.sortSurfaces(self.filledSurfaces)
        self.update()

    def leaveEvent(self, event):
        self.mouseOverSurface = None
        self.update()

    def mouseMoveEvent(self, event):
        y = event.y()
        x = event.x()
        if self.mesial.containsPoint(
                QtCore.QPoint(x, y), QtCore.Qt.OddEvenFill):
            self.mouseOverSurface = self.mesial
            self.update()
        elif self.occlusal.containsPoint(
                QtCore.QPoint(x, y), QtCore.Qt.OddEvenFill):
            self.mouseOverSurface = self.occlusal
            self.update()
        elif self.distal.containsPoint(
                QtCore.QPoint(x, y), QtCore.Qt.OddEvenFill):
            self.mouseOverSurface = self.distal
            self.update()
        elif self.buccal.containsPoint(
                QtCore.QPoint(x, y), QtCore.Qt.OddEvenFill):
            self.mouseOverSurface = self.buccal
            self.update()
        elif self.palatal.containsPoint(
                QtCore.QPoint(x, y), QtCore.Qt.OddEvenFill):
            self.mouseOverSurface = self.palatal
            self.update()

    def mousePressEvent(self, event):
        y = event.y()
        x = event.x()
        if self.mesial.containsPoint(
                QtCore.QPoint(x, y), QtCore.Qt.OddEvenFill):
            if self.isRight:
                self.setFilledSurfaces("D")
            else:
                self.setFilledSurfaces("M")
        elif self.occlusal.containsPoint(
                QtCore.QPoint(x, y), QtCore.Qt.OddEvenFill):
            if self.isBacktooth:
                self.setFilledSurfaces("O")
            else:
                self.setFilledSurfaces("I")
        elif self.distal.containsPoint(
                QtCore.QPoint(x, y), QtCore.Qt.OddEvenFill):
            if not self.isRight:
                self.setFilledSurfaces("D")
            else:
                self.setFilledSurfaces("M")
        elif self.buccal.containsPoint(
                QtCore.QPoint(x, y), QtCore.Qt.OddEvenFill):
            if self.isUpper:
                self.setFilledSurfaces("B")
            else:
                self.setFilledSurfaces("L")
        elif self.palatal.containsPoint(
                QtCore.QPoint(x, y), QtCore.Qt.OddEvenFill):
            if self.isUpper:
                self.setFilledSurfaces("P")
            else:
                self.setFilledSurfaces("B")
        else:
            return  # missed!!
        self.surfaces_changed_signal.emit()

    def resizeEvent(self, event):
        self.shapes()

    def shapes(self):
        self.toothRect = QtCore.QRectF(0, 0, self.width(), self.height())
        irw = self.toothRect.width() * \
            0.25  # inner rectangle width
        if self.isBacktooth:
            irh = self.toothRect.height() * \
                0.25  # backtooth inner rectangle height
        else:
            irh = self.toothRect.height() * \
                0.40  # fronttooth inner rectangle height
        self.innerRect = self.toothRect.adjusted(irw, irh, -irw, -irh)

        self.mesial = QtGui.QPolygon()
        self.mesial.setPoints(
            [0,
             0,
             self.innerRect.topLeft().x(),
             self.innerRect.topLeft().y(),
             self.innerRect.bottomLeft().x(),
             self.innerRect.bottomLeft().y(),
             self.toothRect.bottomLeft().x(),
             self.toothRect.bottomLeft().y()])

        self.occlusal = QtGui.QPolygon()
        self.occlusal.setPoints(
            [self.innerRect.topLeft().x(),
             self.innerRect.topLeft().y(),
             self.innerRect.topRight().x(),
             self.innerRect.topRight().y(),
             self.innerRect.bottomRight().x(),
             self.innerRect.bottomRight().y(),
             self.innerRect.bottomLeft().x(),
             self.innerRect.bottomLeft().y()])

        self.distal = QtGui.QPolygon()
        self.distal.setPoints(
            [self.innerRect.topRight().x(),
             self.innerRect.topRight().y(),
             self.toothRect.topRight().x(),
             self.toothRect.topRight().y(),
             self.toothRect.bottomRight().x(),
             self.toothRect.bottomRight().y(),
             self.innerRect.bottomRight().x(),
             self.innerRect.bottomRight().y()])

        self.buccal = QtGui.QPolygon()
        self.buccal.setPoints(
            [0,
             0,
             self.toothRect.topRight().x(),
             self.toothRect.topRight().y(),
             self.innerRect.topRight().x(),
             self.innerRect.topRight().y(),
             self.innerRect.topLeft().x(),
             self.innerRect.topLeft().y()])

        self.palatal = QtGui.QPolygon()
        self.palatal.setPoints(
            [self.toothRect.bottomLeft().x(),
             self.toothRect.bottomLeft().y(),
             self.innerRect.bottomLeft().x(),
             self.innerRect.bottomLeft().y(),
             self.innerRect.bottomRight().x(),
             self.innerRect.bottomRight().y(),
             self.toothRect.bottomRight().x(),
             self.toothRect.bottomRight().y()])

        self.mouseOverSurface = None  # initiate a value

    def paintEvent(self, event=None):
        '''
        override the paint event so that we can draw our grid
        '''
        if self.isBacktooth:
            if self.isUpper:
                if self.isRight:
                    surfs = "DBPMO"
                else:
                    surfs = "MBPDO"
            else:
                if self.isRight:
                    surfs = "DLBMO"
                else:
                    surfs = "MLBDO"
        else:
            if self.isUpper:
                if self.isRight:
                    surfs = "DBPMI"
                else:
                    surfs = "MBPDI"
            else:
                if self.isRight:
                    surfs = "DLBMI"
                else:
                    surfs = "MLBDI"

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setPen(QtGui.QColor("gray"))
        painter.setBrush(colours.IVORY)
        painter.drawRect(self.toothRect)
        painter.drawRect(self.innerRect)
        painter.drawLine(self.toothRect.topLeft(), self.innerRect.topLeft())
        painter.drawLine(self.toothRect.topRight(), self.innerRect.topRight())
        painter.drawLine(
            self.toothRect.bottomLeft(),
            self.innerRect.bottomLeft())
        painter.drawLine(
            self.toothRect.bottomRight(),
            self.innerRect.bottomRight())
        option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
        rect = self.toothRect.adjusted(0, 0, -self.innerRect.right(), 0)
        painter.drawText(QtCore.QRectF(rect), surfs[0], option)
        rect = self.toothRect.adjusted(0, 0, 0, -self.innerRect.bottom())
        painter.drawText(QtCore.QRectF(rect), surfs[1], option)
        rect = self.toothRect.adjusted(0, self.innerRect.bottom(), 0, 0)
        painter.drawText(QtCore.QRectF(rect), surfs[2], option)
        rect = self.toothRect.adjusted(self.innerRect.right(), 0, 0, 0)
        painter.drawText(QtCore.QRectF(rect), surfs[3], option)
        painter.drawText(QtCore.QRectF(self.innerRect), surfs[4], option)
        painter.setBrush(self.fillcolour)
        if "M" in self.filledSurfaces:
            if self.isRight:
                painter.drawPolygon(self.distal)
            else:
                painter.drawPolygon(self.mesial)
        if "O" in self.filledSurfaces or "I" in self.filledSurfaces:
            painter.drawPolygon(self.occlusal)
        if "D" in self.filledSurfaces:
            if not self.isRight:
                painter.drawPolygon(self.distal)
            else:
                painter.drawPolygon(self.mesial)
        if "B" in self.filledSurfaces:
            if self.isUpper:
                painter.drawPolygon(self.buccal)
            else:
                painter.drawPolygon(self.palatal)
        if "L" in self.filledSurfaces:
                painter.drawPolygon(self.buccal)
        if "P" in self.filledSurfaces:
                painter.drawPolygon(self.palatal)
        if self.mouseOverSurface is not None:
            painter.setBrush(colours.TRANSPARENT)
            painter.setPen(QtGui.QColor("red"))
            painter.drawPolygon(self.mouseOverSurface)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mw = QtWidgets.QMainWindow()
    ui = ToothPropertyEditingWidget()
    ui.setExistingProps("MOD B,GL !COMMENT_TWO ")
    mw.setCentralWidget(ui)
    mw.show()
    sys.exit(app.exec_())
