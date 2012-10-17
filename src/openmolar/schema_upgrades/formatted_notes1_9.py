#! /usr/bin/python

from openmolar import connect
from openmolar.ptModules import notes

def getNotesDict(query_results):
    notes_dict = {}
    ndate, op = "", ""

    #a line is like ('\x01REC\x0c\x08m\x0c\x08m\n\x08',)
    for line, lineno in query_results:
        ntype, note, operator, date2 = notes.decipher_noteline(line)
        if date2 != "":
            ndate = date2
        if operator != "":
            op = operator

        key = (ndate, op)
        if notes_dict.has_key(key):
            notes_dict[key].append((ntype, note))
        else:
            notes_dict[key] = [(ntype, note)]
    return notes_dict

def get_notes(sno):
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute('''SELECT line, lineno from notes where serialno = %s
    order by lineno''', sno)
    results = cursor.fetchall()
    cursor.close()

    notes_dict = getNotesDict(results)

    return notes_dict


def transfer(sno, max_sno):
    print "transferring notes for serialnos %s to %s"% (sno, max_sno)
    while sno <= max_sno:
        print "modding serialno %s"% sno
        notes_dict = get_notes(sno)
        query = '''insert into formatted_notes
        (serialno, ndate, op1 , op2 , ntype, note)
        values (%s, %s, %s, %s, %s, %s)'''

        db = connect.connect()
        cursor = db.cursor()
        for key in notes_dict:
            date, ops = key
            op2=None
            if "/" in ops:
                op1, op2 = ops.split("/")
            else:
                op1=ops

            for ntype, note in notes_dict[key]:
                values = (sno, date, op1, op2, ntype, note)
                db = connect.connect()
                cursor.execute(query, values)
        cursor.close()
        sno += 1

def get_max_sno():
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute("select max(serialno) from notes")
    max_sno = cursor.fetchone()[0]
    cursor.close()
    return max_sno

if __name__ == "__main__":
    max_sno = get_max_sno()
    print "modding notes up to maximum found", max_sno
    transfer(1, max_sno)
    db.close()
