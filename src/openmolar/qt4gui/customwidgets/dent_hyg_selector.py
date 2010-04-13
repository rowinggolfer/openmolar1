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
        self.root.setCheckState(0,2)

        self.dent_root = QtGui.QTreeWidgetItem(self.root, ["All Dentists"])
        self.dent_root.setCheckState(0,2)
        
        self.hyg_root = QtGui.QTreeWidgetItem(self.root, ["All Hygenists"])
        self.hyg_root.setCheckState(0,2)

        self.dent_cbs = {}
        for dent in self.dents:
            i = QtGui.QTreeWidgetItem(self.dent_root, [dent])
            i.setCheckState(0,2)
            self.dent_cbs[dent] = i

        self.hyg_cbs = {}
        for hyg in self.hygs:
            i = QtGui.QTreeWidgetItem(self.hyg_root, [hyg])
            i.setCheckState(0,2)
            self.hyg_cbs[hyg] = i
            
        self.expandAll()
        self.activeDents = dents
        self.activeHygs = hygs
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

    def checkAll(self, checkstate, ignoreHygs=False, ignoreDents=False):
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
        

        self.activeDents = []
        self.activeHygs = []

        allDentsChecked = 2
        for dent in self.dent_cbs:
            if self.dent_cbs[dent].checkState(0):
                self.activeDents.append(dent)
            else:
                allDentsChecked = 0

        allHygsChecked = 2
        for hyg in self.hyg_cbs:
            if self.hyg_cbs[hyg].checkState(0):
                self.activeHygs.append(hyg)
            else:
                allHygsChecked = 0
        
        self.dent_root.setCheckState(0, allDentsChecked)
        self.hyg_root.setCheckState(0, allHygsChecked)

        allClinicians = 2 if allDentsChecked and allHygsChecked else 0
        
        self.root.setCheckState(0, allClinicians)

        self.signals(True)
        
        self.emit(QtCore.SIGNAL("selectionChanged"))

    def getActiveDents(self):
        return self.activeDents

    def getActiveHygs(self):
        return self.activeHygs

    def getActiveClinicians(self):
        return self.activeDents + self.activeHygs
    
                                
if __name__ == "__main__":
    app = QtGui.QApplication([])
    dents = ["Neil","Bea","Helen", "Andy"]
    hygs = ["Rosie", "Sally", "Ariana"]
    w = dentHygSelector(dents, hygs)
    w.show()
    app.exec_()
