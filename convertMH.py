'''
this script helps the user modify the mednotes table.
for over a decade, we had to use the "allergies" field to alert us to 
important conditions.

I have added a new field "alert" 
'''
import os,sys,datetime
from PyQt4 import QtGui, QtCore

wkdir=os.path.dirname(os.getcwd())
sys.path.append(wkdir)


from openmolar.settings import localsettings
from openmolar.qt4gui.dialogs import Ui_medhist
from openmolar.dbtools import updateMH
from openmolar.connect import connect

progressFile=os.path.join(localsettings.localFileDirectory,"mh_progression.txt")

def showDialog(Dialog,serialno,data):
    def clearAllerg():
        dl.allergies_lineEdit.setText("")
    def transferToMemo():
        db=connect()
        cursor=db.cursor()
        cursor.execute("select memo from patients where serialno=%d"%serialno)
        existing=cursor.fetchone()[0]
        memo="%s (from mh-%s)"%(existing,dl.allergies_lineEdit.text())
        memo=memo.replace('"','\"')
        cursor.execute('update patients set memo="%s" where serialno=%d'%(memo,serialno))
        cursor.close()
        db.commit()
        dl.allergies_lineEdit.setText("")
    
    dl = Ui_medhist.Ui_Dialog()
    dl.setupUi(Dialog)
    Dialog.setWindowTitle("Medical notes for patient number %s"%serialno)
        
    Dialog.connect(dl.clear_pushButton,QtCore.SIGNAL("clicked()"),clearAllerg)
    Dialog.connect(dl.transfer_pushButton,QtCore.SIGNAL("clicked()"),transferToMemo)

    chkdate=None
    alert=False
    if data != None:
        item=0
        for lineEdit in (
        dl.doctor_lineEdit,
        dl.doctorAddy_lineEdit,
        dl.curMeds_lineEdit,
        dl.pastMeds_lineEdit,
        dl.allergies_lineEdit,
        dl.heart_lineEdit,
        dl.lungs_lineEdit,
        dl.liver_lineEdit,
        dl.bleeding_lineEdit,
        dl.kidneys_lineEdit,
        dl.anaesthetic_lineEdit,
        dl.other_lineEdit
        ):
            lineEdit.setText(data[item])
            item+=1
        alert=data[12]
        chkdate=data[13]
        
    if chkdate:
        dl.dateEdit.setDate(chkdate)
    else:
        dl.date_label.hide()
        dl.dateEdit.hide()
    dl.checkBox.setChecked(alert)
    
    if Dialog.exec_():
        newdata=[]
        for lineEdit in (
        dl.doctor_lineEdit,
        dl.doctorAddy_lineEdit,
        dl.curMeds_lineEdit,
        dl.pastMeds_lineEdit,
        dl.allergies_lineEdit,
        dl.heart_lineEdit,
        dl.lungs_lineEdit,
        dl.liver_lineEdit,
        dl.bleeding_lineEdit,
        dl.kidneys_lineEdit,
        dl.anaesthetic_lineEdit,
        dl.other_lineEdit
        ):
            newdata.append(str(lineEdit.text().toAscii()))
        newdata.append(dl.checkBox.isChecked())
        chkdate=dl.dateEdit.date().toPyDate()
        if chkdate!=datetime.date(1900,1,1):
            newdata.append(dl.dateEdit.date().toPyDate())
        else:
            newdata.append(None)
        result=tuple(newdata)
        if data!=result:
            print "MH changed"
            if not updateMH.write(serialno,result):
                QtGui.QMessageBox.error("unable to change serialno %d<br />Quitting"%serialno)
                return False
        else:
            print "unchanged"
        return True
    else:
        return False
    

def main():
    db=connect()
    cursor=db.cursor()

    try:
        f=open(progressFile,"r")
        start=int(f.read())
        f.close()
        print "starting at patient no %d"%start
    except:
        start=0

    cursor.execute('select serialno from mednotes where serialno>%d'%start)
    histories=cursor.fetchall()

    for history in histories:
        serialno=history[0]
        print serialno
        cursor.execute('''select drnm,adrtel,curmed,oldmed,allerg,heart,
        lungs,liver,kidney,bleed,anaes,other,alert,chkdate from mednotes 
        where serialno=%d'''%serialno)
        MH=cursor.fetchone()
        if not MH[4].lower() in ("","med ok","ok","nad"):
            Dialog = QtGui.QDialog()
            if not showDialog(Dialog,serialno,MH):
                result=QtGui.QMessageBox.question(Dialog,"confirm","Quit now?",
                QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
                
                if result==QtGui.QMessageBox.Yes:
                    break
        f=open(progressFile,"w")
        f.write(str(serialno))
        f.close()
            
    cursor.close()
    db.commit()


if __name__=="__main__":
    app=QtGui.QApplication([])
    main()    