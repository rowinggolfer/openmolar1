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

backToothCodes = (
    "+P", "+S", "AP", "AT", "B", "B,AM", "B,CO", "B,CO,CT", "B,CO,PR", "B,CT",
    "B,CT,CO", "B,GL", "BD", "BDLOM,CO,PR", "BM", "BM,CO", "BMO", "BMODP",
    "BMOL,CO", "BO", "BO,AM", "BO,CO", "BO,GL", "BOL", "BOM", "BR/CR,A1",
    "BR/CR,A2", "BR/CR,OT", "BR/CR,V1", "BR/CR,V1,PR", "BR/P,A2", "BR/P,OT",
    "BR/P,V1", "CR,OPAL", "CR,OPALITE", "CR,LAVA", "CR,EMAX", "CR,EVEREST",
    "CR,FORT", "CR,A1", "CR,A1,C4", "CR,A1,PR", "CR,A2", "CR,GO",
    "CR,GO,PR", "CR,OT", "CR,OT,C4", "CR,P1", "CR,P1,C3", "CR,PJ", "CR,V1",
    "CR,V1,C1", "CR,V1,C2", "CR,V1,C3", "CR,V1,PR", "CR,V2", "CR/MODB,GO",
    "CR/MODL,GO", "CR/MODP,GO", "D", "D,AM", "D,CO", "D,GL", "DB", "DB,AM",
    "DB,CO", "DB,CT,CO", "DB,GL", "DBM,CO", "DBO", "DBO,CO", "DL", "DL,CO",
    "DL,GL", "DMO", "DO", "DO,AM", "DO,CO", "DO,GL", "DO,PR", "DOB", "DOB,AM",
    "DOB,CO", "DOB,GL", "DOB,PR", "DOB,PR,CO", "DOBL", "DOBL,PR", "DOBM,CO",
    "DOBM,GL", "DOBP,CO", "DOL", "DOL,CO", "DOL,CO,PR", "DOL,GL", "DOL,PR",
    "DOLB", "DOM", "DOM,CO", "DOMB", "DOML,PR", "DOMP,CO", "DOP", "DOP,AM",
    "DOP,CO", "DOP,CO,PR", "DOP,GL", "DOP,PR",
    "DOP,PR,CO", "DOPM", "DP", "DP,CO", "DP,CT,CO", "DP,GL", "DR", "FA",
    "FS", "FS,CO", "FS,CO.", "FS,GC", "FS,GL", "GC/DO", "GC/DOL", "GC/MO",
    "GC/MOD", "GC/MODB", "GC/MODL", "GC/MODP", "GI/DO", "GI/DOBL", "GI/DOL",
    "GI/MO", "GI/MOD", "GI/MODP", "IM", "L", "L,AM", "L,CO", "L,GL", "LD",
    "LMBO,GL", "LO", "LO,CO", "LO,GL", "LOM,CO", "M", "M,CO", "M,CO,PR",
    "M,GL", "MB", "MB,CO", "MB,CT,CO", "MB,GL", "MBD", "MBD,CO", "MDOB",
    "MDOL", "MDOL,CO", "ML", "ML,CO", "ML,GL", "MLODB,CO", "MLODB,CO,PR", "MO",
    "MO,AM", "MO,CO", "MO,GL", "MO,PR", "MOB", "MOB,AM", "MOB,CO", "MOB,GL",
    "MOB,PR", "MOB,PR,CO", "MOBD,CO", "MOBL", "MOBL,CO,PR", "MOBP", "MOBP,CO",
    "MOBPD", "MOD", "MOD,AM", "MOD,CO", "MOD,CO,PR", "MOD,GL", "MOD,PR",
    "MODB", "MODB,AM", "MODB,CO", "MODB,CO,PR", "MODB,GL", "MODB,GL,CO",
    "MODB,PR", "MODB,PR,CO", "MODB,PR,GL", "MODBL", "MODBL,CO", "MODBL,GL",
    "MODBL,PR", "MODBP", "MODBP,CO", "MODBP,CO,PR", "MODBP,GL", "MODL",
    "MODL,CO", "MODL,CO,PR", "MODL,GL", "MODL,PR", "MODLB", "MODLB,CO", "MODP",
    "MODP,AM", "MODP,AM,CO", "MODP,CO", "MODP,CO,PR", "MODP,GL",
    "MODP,GL,CO", "MODP,GL,PR", "MODP,PR", "MODP,PR,CO", "MODPB", "MODPB,CO",
    "MOL", "MOL,CO", "MOL,GL", "MOL,PR", "MOL,PR,CO", "MOLD",
    "MOLD,CO", "MOP", "MOP,CO", "MOP,GL", "MOP,PR,CO", "MOPB", "MOPD",
    "MOPDB,PR", "MP", "MP,AM", "MP,CO", "MP,CT,CO", "MP,GL", "O", "O,AM",
    "O,CO", "O,GL", "OB", "OB,AM", "OB,CO", "OB,GL", "OB,GL,CO", "OB,PR", "OD",
    "ODB,CO", "OE", "OL", "OL,CO", "OL,GL", "OL,GL,GL", "OL,PR", "OM",
    "OMD", "OML", "OP", "OP,CO", "OP,CO,PR", "OP,GL", "OP,PR", "OPB",
    "P", "P,AM", "P,CO", "P,CO,PR", "P,CT,CO", "P,CT,PR,CO", "P,GL", "PD",
    "PE", "PI/", "PI/DO", "PI/DOB", "PI/DOL", "PI/LOB", "PI/MO", "PI/MOB",
    "PI/MOD", "PI/MODB", "PI/MODBL", "PI/MODBP", "PI/MODL", "PI/MODP",
    "PI/MODPB", "PI/MOL", "PI/MOPB", "PI/O", "PI/OB", "PO", "PO,CO", "PO,GL",
    "PV", "RP", "RT", "TM", "TR/M", "UE")

frontToothCodes = (
    "+P", "+S", "-D,2", "-M,1", "-M,2", "AP", "AP,RR",
    "AT", "B", "B,AM", "B,AM'", "B,CO", "B,GL", "B,PR", "BD",
    "BD,AM", "BD,CO", "BDL", "BDLMI,PR", "BDP", "BI", "BIDM", "BIM",
    "BIP", "BLMD", "BM", "BM,CO", "BM,GL", "BMD", "BMI", "BMIDI",
    "BMLD,CO", "BMP", "BP", "BP,AM", "BPDM", "BR,RA", "BR/CR,A1",
    "BR/CR,A1,C4", "BR/CR,A2", "BR/CR,GO", "BR/CR,OT", "BR/CR,V1",
    "BR/CR,V1,C1", "BR/CR,V1,C2", "BR/CR,V1,C3", "BR/CR,V1,C4",
    "BR/CR,V1,PR", "BR/CR,V2", "BR/GI/DP", "BR/GI/MPD", "BR/MR", "BR/P,A1",
    "BR/P,A2", "BR/P,AE", "BR/P,MA", "BR/P,OT", "BR/P,PO", "BR/P,RA",
    "BR/P,RO", "BR/P,V1", "BR/P,V2", "CR,A1", "CR,A1,C1", "CR,A1,C2", "CR,A2",
    "CR,GO", "CR,OT", "CR,OT,C1", "CR,OT,C2", "CR,OT,C3", "CR,OT,PR", "CR,P1",
    "CR,PJ", "CR,PJ,C1", "CR,PJ,C2", "CR,PJ,C3", "CR,PJ,C4", "CR,PJ,PR",
    "CR,V1", "CR,V1,C1", "CR,V1,C2", "CR,V1,C3", "CR,V1,C4", "CR,V1,PR",
    "CR,V2", "CR,V2,C2", "CR,V2,C3,PR", "CR,V2,C4,PR", "CR,V2,PR",
    "CR,V2,PR,C3", "CR/MPD,GO", "D", "D,AM", "D,AM'",
    "D,CO", "D,GL", "D,PR", "DB", "DB,AM", "DB,CO", "DB,GL", "DBI",
    "DBM", "DBM,AM", "DBPI,PR", "DI", "DI,A", "DI,A,PR", "DI,AM", "DI,CO",
    "DI,CO,PR", "DI,GL", "DI,PR", "DIB", "DIB,CO", "DIB,GL", "DIBM",
    "DIBM,GL,PR", "DIBP", "DIL", "DIL,PR", "DILB", "DILM", "DIMBP", "DIMI",
    "DIMP", "DIP", "DIP,CO", "DIP,GL", "DIP,PR", "DIPB", "DIPMB", "DL",
    "DL,AM", "DL,CO", "DL,GL", "DLBI", "DLI", "DLM", "DMB", "DMIBP", "DP",
    "DP,AM", "DP,AM'", "DP,AM]", "DP,CO", "DP,GL", "DPB", "DPI", "DPIB,PR",
    "DPM,CO", "DPMI", "DR", "FA", "FS/P", "FS/P,GL", "GI/B", "GI/DBP",
    "GI/DI", "GI/DIL", "GI/DIP", "GI/DL", "GI/M", "GI/MI", "GI/MIDL",
    "GI/MIDP", "GI/MIL", "GI/MIP", "GI/MIPD", "GI/MLD", "GI/MPDI", "GI/P",
    "I", "I,AM", "I,CO", "I,GL", "IM", "L", "L,AM", "L,CO", "L,GL", "LD,AM",
    "LD,GL", "LI", "LI,CO", "LIM", "M", "M,AM", "M,CO", "M,GL",
    "M,PR", "MB", "MB,AM", "MB,CO", "MB,GL", "MB,PR", "MB,PR,CO", "MBD",
    "MBD,GL", "MBDI", "MBDL", "MBDP", "MBI", "MBI,GL", "MBP", "MBPI",
    "MDB", "MDB,CO", "MDB,GL", "MDBL,PR", "MDBP,GL", "MDBP,PR", "MDBPI",
    "MDIB,PR", "MDL", "MDLB,GL", "MDP", "MDPB", "MDPBI", "MDPIB", "MI",
    "MI,AM", "MI,CO", "MI,GL", "MI,PR", "MI,PR,CO", "MIB", "MIB,PR", "MIBD",
    "MIBD,GL", "MIBD,PR", "MIBDI,PR", "MIBDP", "MIBLD", "MIBP", "MIBP,PR",
    "MIBPD", "MIBPD,CO", "MIBPD,PR", "MIDB", "MIDB,CO", "MIDB,PR", "MIDBL",
    "MIDBL,CO,PR", "MIDBP", "MIDBP,CO", "MIDBP,GL", "MIDBP,PR", "MIDI",
    "MIDI,CO", "MIDIB", "MIDL", "MIDLB,CO", "MIDP",
    "MIDPB", "MIDPB,PR", "MIL", "MIL,GL", "MIL,PR", "MILD", "MIP", "MIP,CO",
    "MIP,GL", "MIP,PR", "MIPB", "MIPB,CO,PR", "MIPB,PR", "MIPBD", "MIPBD,CO",
    "MIPBD,PR", "MIPD", "MIPDB", "MIPDB,PR", "MIPID", "ML", "ML,GL", "MLD",
    "MLDI", "MLI", "MP", "MP,AM", "MP,CO", "MP,GL", "MPB", "MPD", "MPD,CO",
    "MPD,GL", "MPDB", "MPI", "MPID,GL", "O", "O,CO", "O,GL", "P",
    "P,AM", "P,CO", "P,GL", "P,PR", "PB", "PB,GL", "PD", "PD,AM",
    "PD,GL", "PDB", "PDB,GL", "PDI", "PE", "PI", "PI,GL", "PI/B",
    "PI/MBDL", "PI/MBPD", "PI/MDBL", "PI/MDBP", "PI/MDLB", "PI/MDPB",
    "PI/MIDB", "PIB", "PID,CO", "PIM", "PM", "PM,GL", "PMB", "PMI", "PMID",
    "PV", "RI", "RP", "RT", "TM", "UE", "VP",
    "CR,OPAL", "CR,OPALITE",
    "CR,LAVA", "CR,EMAX", "CR,EVEREST", "CR,FORT",)

treatment_only = (
    "EX",
    "EX/S1",
    "EX/S2",
    "CR,RC",
    "PX",
    "PX+",
    "ST")  # not exhaustive


if __name__ == "__main__":
    print("Unique to FrontTeeth")
    for a in frontToothCodes:
        if not a in backToothCodes:
            print(a, end=' ')

    print("Unique to BackTeeth")
    for a in backToothCodes:
        if not a in frontToothCodes:
            print(a, end=' ')
