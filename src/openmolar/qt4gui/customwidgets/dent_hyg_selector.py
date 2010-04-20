# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for
# more details.

from PyQt4 import QtGui, QtCore

class dentHygSelector(QtGui.QTreeWidget):
    def __init__(self, dents, hygs):
        QtGui.QTreeWidget.__init__(self)
        self.setHeaderHidden(True)
        self.dents = dents
        self.hygs = hygs
        self.root = QtGui.QTreeWidgetItem(self, ["All Clinicians"])
        self.root.setCheckState(0, QtCore.Qt.Checked)

        self.dent_root = QtGui.QTreeWidgetItem(self.root, ["All Dentists"])
        self.dent_root.setCheckState(0, QtCore.Qt.Checked)
        
        self.hyg_root = QtGui.QTreeWidgetItem(self.root, ["All Hygenists"])
        self.hyg_root.setCheckState(0, QtCore.Qt.Checked)

        self.dent_cbs = {}
        for dent in self.dents:
            i = QtGui.QTreeWidgetItem(self.dent_root, [dent])
            i.setCheckState(0, QtCore.Qt.Checked)
            self.dent_cbs[dent] = i

        self.hyg_cbs = {}
        for hyg in self.hygs:
            i = QtGui.QTreeWidgetItem(self.hyg_root, [hyg])
            i.setCheckState(0, QtCore.Qt.Checked)
            self.hyg_cbs[hyg] = i
            
        self.expandAll()
        self.selectedDents = dents
        self.selectedHygs = hygs
        self.signals(True)

    def signals(self, connect):
        if connect:
            self.connect(self,
            QtCore.SIGNAL("itemChanged (QTreeWidgetItem *,int)"), 
            self.interact)
        else:
            self.disconnect(self,
            QtCore.SIGNAL("itemChanged (QTreeWidgetItem *,int)"), 
            self.interact)

    def checkAll(self, checkstate=QtCore.Qt.Checked, 
    ignoreHygs=False, ignoreDents=False):
        if not ignoreHygs:
            for hyg in self.hyg_cbs.values():
                hyg.setCheckState(0, checkstate)
        if not ignoreDents:
            for dent in self.dent_cbs.values():
                dent.setCheckState(0, checkstate)
        
                            
    def interact(self, item, column):
        self.signals(False)

        if item == self.root:
            self.checkAll(self.root.checkState(0))
        elif item == self.dent_root:
            self.checkAll(self.dent_root.checkState(0), ignoreHygs=True)
        elif item == self.hyg_root:
            self.checkAll(self.hyg_root.checkState(0), ignoreDents=True)
        

        self.selectedDents = []
        self.selectedHygs = []

        allDentsChecked = QtCore.Qt.Checked
        for dent in self.dent_cbs:
            if self.dent_cbs[dent].checkState(0):
                self.selectedDents.append(dent)
            else:
                allDentsChecked = QtCore.Qt.Unchecked

        allHygsChecked = QtCore.Qt.Checked
        for hyg in self.hyg_cbs:
            if self.hyg_cbs[hyg].checkState(0):
                self.selectedHygs.append(hyg)
            else:
                allHygsChecked = QtCore.Qt.Unchecked
        
        self.dent_root.setCheckState(0, allDentsChecked)
        self.hyg_root.setCheckState(0, allHygsChecked)

        if allDentsChecked and allHygsChecked:
            allClinicians = QtCore.Qt.Checked
        else:
            allClinicians = QtCore.Qt.Unchecked
        
        self.root.setCheckState(0, allClinicians)

        self.signals(True)
        self.emit(QtCore.SIGNAL("selectionChanged"))
            
    def getSelectedDents(self):
        return self.selectedDents

    def getSelectedHygs(self):
        return self.selectedHygs

    def getSelectedClinicians(self):
        return self.selectedDents + self.selectedHygs
    
    def allChecked(self):
        return self.root.checkState(0) == QtCore.Qt.Checked
                                
if __name__ == "__main__":
    app = QtGui.QApplication([])
    dents = ["Neil","Bea","Helen", "Andy"]
    hygs = ["Rosie", "Sally", "Ariana"]
    w = dentHygSelector(dents, hygs)
    w.show()
    app.exec_()
