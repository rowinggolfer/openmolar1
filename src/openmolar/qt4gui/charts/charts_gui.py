# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
provides some logic functions for the charts within openmolar gui.
'''

from __future__ import division
import copy

from PyQt4 import QtGui, QtCore
from openmolar.settings import localsettings
from openmolar.qt4gui.fees import course_module

def navigateCharts(om_gui, direction):
    '''
    called by a keypress in the tooth prop LineEdit or a click on one of
    the tooth prop buttons.
    entry will have been checked.
    '''
    [x, y] = om_gui.ui.staticChartWidget.selected

    if y == 0:
        #--upper teeth
        if direction == "up":
            if x != 0:
                x -= 1
        else:
            if x == 15:
                x, y = 15, 1
            else:
                x += 1
    else:
        #--lower teeth
        if direction == "up":
            if x == 15:
                x, y=15, 0
            else:
                x += 1
        else:
            if x != 0:
                x -= 1

    selectChartedTooth(om_gui, x, y)
    tooth = om_gui.ui.staticChartWidget.grid[y][x]

    row = (16*y) + x

    om_gui.ui.chartsTableWidget.setCurrentCell(row, 0)
    om_gui.ui.toothPropsWidget.setTooth(tooth, om_gui.selectedChartWidget)

def chart_navigate(om_gui):
    '''
    this is called when the tooth props widget
    static/plan/completed buttons are used
    '''
    row=om_gui.ui.chartsTableWidget.currentRow()

    tString = str(om_gui.ui.chartsTableWidget.item(
    row, 0).text().toAscii())
    
    om_gui.ui.toothPropsWidget.setTooth(tString, om_gui.selectedChartWidget)
    chartNavigation(om_gui, [tString], True)

def deleteComments(om_gui):
    '''
    called when user has trigger deleted comments in the toothProp
    '''
    tooth = str(om_gui.ui.chartsTableWidget.item(
    om_gui.ui.chartsTableWidget.currentRow(), 0).text())

    if tooth in om_gui.ui.staticChartWidget.commentedTeeth:
        om_gui.ui.staticChartWidget.commentedTeeth.remove(tooth)
        om_gui.ui.staticChartWidget.update()
    existing = om_gui.pt.__dict__[tooth+"st"]
    om_gui.pt.__dict__[tooth+"st"] = re.sub("![^ ]* ","",existing)

def updateCharts(om_gui, arg):
    '''
    called by a signal from the toothprops widget -
    args are the new tooth properties eg modbl,co
    '''
    try:
        tooth = str(om_gui.ui.chartsTableWidget.item(
        om_gui.ui.chartsTableWidget.currentRow(), 0).text())
    except AttributeError:
        return
    #print "update charts called with arg '%s'"% arg,
    #print "tooth is ",tooth
    if om_gui.selectedChartWidget == "st":
        om_gui.pt.__dict__[tooth + om_gui.selectedChartWidget] = arg
        #--update the patient!!
        om_gui.ui.staticChartWidget.setToothProps(tooth, arg)
        om_gui.ui.summaryChartWidget.setToothProps(tooth, arg)
        om_gui.ui.staticChartWidget.update()
    elif om_gui.selectedChartWidget == "pl":
        if arg != "" and course_module.newCourseNeeded(om_gui):
            return
        om_gui.toothTreatAdd(tooth, arg)
        om_gui.ui.planChartWidget.update()

    elif om_gui.selectedChartWidget == "cmp":
        om_gui.advise('<p>'+_('''for the moment, please enter treatment
into the plan first then complete it.''')+'</p>', 1)
    else:
        om_gui.advise(_("unable to update chart - this shouldn't happen!!"),
        2) #--should NEVER happen

def updateChartsAfterTreatment(om_gui, tooth, newplan, newcompleted):
    '''
    update the charts when a planned item has moved to completed
    '''
    #print "update charts after treatment", tooth, newplan, newcompleted
    om_gui.ui.planChartWidget.setToothProps(tooth, newplan)
    om_gui.ui.planChartWidget.update()
    om_gui.ui.completedChartWidget.setToothProps(tooth, newcompleted)
    om_gui.ui.completedChartWidget.update()

def flipDeciduous(om_gui):
    '''
    change a tooth state from deciduous to permanent
    or back again
    '''
    if om_gui.selectedChartWidget == "st":
        selectedCells = om_gui.ui.chartsTableWidget.selectedIndexes()
        for cell in selectedCells:
            row=cell.row()
            selectedTooth=str(
            om_gui.ui.chartsTableWidget.item(row, 0).text().toAscii())

            #print "flipping tooth ", selectedTooth
            om_gui.pt.flipDec_Perm(selectedTooth)
        for chart in (om_gui.ui.staticChartWidget, om_gui.ui.planChartWidget,
        om_gui.ui.completedChartWidget, om_gui.ui.perioChartWidget,
        om_gui.ui.summaryChartWidget):
            chart.chartgrid=om_gui.pt.chartgrid
            #--necessary to restore the chart to full dentition
            chart.update()
    else:
        om_gui.advise(
        _("you need to be in the static chart to change tooth state"), 1)

def checkPreviousEntry(om_gui):
    '''
    check to see if the toothProps widget has unfinished business
    '''
    if not om_gui.ui.toothPropsWidget.lineEdit.unsavedChanges():
        return True
    else:
        return om_gui.ui.toothPropsWidget.lineEdit.additional()
    
def chartTableNav(om_gui, row, col, row1, col1):
    '''
    charts table has been navigated
    '''
    if localsettings.debug:
        #print "UNUSED chartTableNav", row,col,row1,col1
        pass

def chartNavigation(om_gui, teeth, callerIsTable=False):
    '''
    one way or another, a tooth has been selected...
    this updates all relevant widgets
    '''
    #--called by a navigating a chart or the underlying table
    #--convert from QString
    #print "chartNavigation", teeth, callerIsTable
    grid = (["ur8", "ur7", "ur6", "ur5", 'ur4', 'ur3', 'ur2', 'ur1',
    'ul1', 'ul2', 'ul3', 'ul4', 'ul5', 'ul6', 'ul7', 'ul8'],
    ["lr8", "lr7", "lr6", "lr5", 'lr4', 'lr3', 'lr2', 'lr1',
    'll1', 'll2', 'll3', 'll4', 'll5', 'll6', 'll7', 'll8'])

    if teeth == []:
        print '''chartNavigation called with teeth=[]\n
        THIS SHOULDN'T HAPPEN!!!!'''
        return
    tooth = teeth[0]

    om_gui.ui.toothPropsWidget.setTooth(tooth, om_gui.selectedChartWidget)

    #--calculate x, y co-ordinates for the chartwidgets
    if tooth in grid[0]:
        y = 0
    else:
        y = 1
    x = grid[y].index(tooth)

    selectChartedTooth(om_gui, x, y)
    om_gui.ui.chartsTableWidget.setCurrentCell(x+y*16, 0)
    for tooth in teeth:
        #other teeth have been selected
        #ie. ctrl-click or shift ciick
        if tooth in grid[0]:
            y = 0
        else:
            y = 1
        x = grid[y].index(tooth)

        om_gui.ui.chartsTableWidget.setCurrentCell(x+y*16, 0,
        QtGui.QItemSelectionModel.Select)

def selectChartedTooth(om_gui, x, y):
    '''
    only one tooth can be 'selected'
    '''
    om_gui.ui.planChartWidget.setSelected(x, y, showSelection =
    om_gui.selectedChartWidget == "pl")

    om_gui.ui.completedChartWidget.setSelected(x, y, showSelection =
    om_gui.selectedChartWidget == "cmp")

    om_gui.ui.staticChartWidget.setSelected(x, y, showSelection =
    om_gui.selectedChartWidget == "st")


def bpe_dates(om_gui):
    '''
    updates the date in the bpe date groupbox
    '''
    #--bpe = "basic periodontal exam"
    om_gui.ui.bpeDateComboBox.clear()
    om_gui.ui.bpe_textBrowser.setPlainText("")
    if om_gui.pt.bpe == []:
        om_gui.ui.bpeDateComboBox.addItem(QtCore.QString("NO BPE"))
    else:
        l = copy.deepcopy(om_gui.pt.bpe)
        l.reverse() #show newest first
        for sets in l:
            bpedate = localsettings.formatDate(sets[0])
            om_gui.ui.bpeDateComboBox.addItem(bpedate)

def bpe_table(om_gui, arg):
    '''
    updates the BPE chart on the clinical summary page
    '''
    if om_gui.pt.bpe != []:
        last_bpe_date = localsettings.formatDate(om_gui.pt.bpe[-1][0])
        om_gui.ui.bpe_groupBox.setTitle("BPE " + last_bpe_date)
        l=copy.deepcopy(om_gui.pt.bpe)
        l.reverse()
        bpestring=l[arg][1]
        bpe_html='<table width="100%" border="1"><tr>'
        for i in range(len(bpestring)):
            if i == 3:
                bpe_html+="</tr><tr>"
            bpe_html+='<td align="center">%s</td>'%bpestring[i]
        for i in range(i+1, 6):
            if i == 3:
                bpe_html+="</tr><tr>"
            bpe_html+='<td align="center">_</td>'
        bpe_html+='</tr></table>'
        om_gui.ui.bpe_textBrowser.setHtml(bpe_html)
    else:
        #--necessary in case of the "NO DATA FOUND" option
        om_gui.ui.bpe_groupBox.setTitle(_("BPE"))
        om_gui.ui.bpe_textBrowser.setHtml("")

def periochart_dates(om_gui):
    '''
    multiple perio charts on multiple dates....
    display those dates in a combo box
    '''
    om_gui.ui.perioChartDateComboBox.clear()
    for date in om_gui.pt.perioData.keys():
        om_gui.ui.perioChartDateComboBox.addItem(QtCore.QString(date))
    if om_gui.pt.perioData == {}:
        om_gui.ui.perioChartDateComboBox.addItem(_("NO CHARTS"))

def layoutPerioCharts(om_gui):
    '''
    layout the perio charts
    '''
    #--convert from QString
    selected_date=str(om_gui.ui.perioChartDateComboBox.currentText())
    if om_gui.pt.perioData.has_key(selected_date):
        perioD = om_gui.pt.perioData[selected_date]
        #--headers=("Recession", "Pocketing", "Plaque", "Bleeding", "Other",
        #--"Suppuration", "Furcation", "Mobility")
        for key in perioD.keys():
            for i in range(8):
                om_gui.ui.perioChartWidgets[i].setProps(key, perioD[key][i])
    else:
        om_gui.advise("no perio data found for", selected_date)
        for i in range(8):
            om_gui.ui.perioChartWidgets[i].props = {}
    for chart in om_gui.ui.perioChartWidgets:
        chart.update()

def chartsTable(om_gui):
    '''
    update the charts table
    '''
    #print "filling chartsTable"
    om_gui.advise("filling charts table")
    om_gui.ui.chartsTableWidget.clear()
    om_gui.ui.chartsTableWidget.setSortingEnabled(False)
    om_gui.ui.chartsTableWidget.setRowCount(32)
    headers=["Tooth", "Deciduous", "Static", "Plan", "Completed"]
    om_gui.ui.chartsTableWidget.setColumnCount(5)
    om_gui.ui.chartsTableWidget.setHorizontalHeaderLabels(headers)
    om_gui.ui.chartsTableWidget.verticalHeader().hide()

    for chart in (om_gui.ui.summaryChartWidget,
    om_gui.ui.staticChartWidget,
    om_gui.ui.planChartWidget,
    om_gui.ui.completedChartWidget,
    om_gui.ui.perioChartWidget):
        chart.chartgrid=om_gui.pt.chartgrid
        #--sets the tooth numbering
    row=0

    for tooth in ("ur8", "ur7", "ur6", "ur5", 'ur4', 'ur3', 'ur2', 'ur1',
        'ul1', 'ul2', 'ul3', 'ul4', 'ul5', 'ul6', 'ul7', 'ul8',
        "lr8", "lr7", "lr6", "lr5", 'lr4', 'lr3', 'lr2', 'lr1',
        'll1', 'll2', 'll3', 'll4', 'll5', 'll6', 'll7', 'll8'):
        item1=QtGui.QTableWidgetItem(tooth)
        static_text=om_gui.pt.__dict__[tooth+"st"]
        staticitem=QtGui.QTableWidgetItem(static_text)
        decidousitem=QtGui.QTableWidgetItem(om_gui.pt.chartgrid[tooth])
        om_gui.ui.chartsTableWidget.setRowHeight(row, 15)
        om_gui.ui.chartsTableWidget.setItem(row, 0, item1)
        om_gui.ui.chartsTableWidget.setItem(row, 1, decidousitem)
        om_gui.ui.chartsTableWidget.setItem(row, 2, staticitem)
        row += 1
        om_gui.ui.summaryChartWidget.setToothProps(tooth, static_text)
        om_gui.ui.staticChartWidget.setToothProps(tooth, static_text)
        pItem = om_gui.pt.__dict__[tooth+"pl"]
        cItem = om_gui.pt.__dict__[tooth+"cmp"]
        planitem = QtGui.QTableWidgetItem(pItem)
        cmpitem = QtGui.QTableWidgetItem(cItem)
        om_gui.ui.chartsTableWidget.setItem(row, 3, planitem)
        om_gui.ui.chartsTableWidget.setItem(row, 4, cmpitem)
        om_gui.ui.planChartWidget.setToothProps(tooth, pItem.lower())
        om_gui.ui.completedChartWidget.setToothProps(tooth, cItem.lower())

        if static_text[:2] in ("AT", "TM", "UE"):
            om_gui.ui.perioChartWidget.setToothProps(tooth, static_text)
    om_gui.ui.chartsTableWidget.resizeColumnsToContents()
    om_gui.ui.chartsTableWidget.setCurrentCell(0, 0)
