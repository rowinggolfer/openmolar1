#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ############################################################################ #
# #                                                                          # #
# # Copyright (c) 2009-2014 Neil Wallace <neil@openmolar.com>                # #
# #                                                                          # #
# # This file is part of OpenMolar.                                          # #
# #                                                                          # #
# # OpenMolar is free software: you can redistribute it and/or modify        # #
# # it under the terms of the GNU General Public License as published by     # #
# # the Free Software Foundation, either version 3 of the License, or        # #
# # (at your option) any later version.                                      # #
# #                                                                          # #
# # OpenMolar is distributed in the hope that it will be useful,             # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of           # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            # #
# # GNU General Public License for more details.                             # #
# #                                                                          # #
# # You should have received a copy of the GNU General Public License        # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.       # #
# #                                                                          # #
# ############################################################################ #

from openmolar.qt4gui.dialogs import saveMemo
from openmolar.qt4gui.dialogs import permissions
from openmolar.qt4gui.dialogs import select_language

from openmolar.qt4gui.dialogs.newBPE import BPE_Dialog
from openmolar.qt4gui.dialogs.assistant_select_dialog import AssistantSelectDialog
from openmolar.qt4gui.dialogs.clinician_select_dialog import ClinicianSelectDialog
from openmolar.qt4gui.dialogs.duplicate_receipt_dialog import DuplicateReceiptDialog
from openmolar.qt4gui.dialogs.save_discard_cancel import SaveDiscardCancelDialog
from openmolar.qt4gui.dialogs.med_notes_dialog import MedNotesDialog
from openmolar.qt4gui.dialogs.choose_tooth_dialog import ChooseToothDialog
from openmolar.qt4gui.dialogs.exam_wizard import ExamWizard
from openmolar.qt4gui.dialogs.hygTreatWizard import HygTreatWizard
from openmolar.qt4gui.dialogs.recall_dialog import RecallDialog
from openmolar.qt4gui.dialogs.child_smile_dialog import ChildSmileDialog
from openmolar.qt4gui.dialogs.alter_todays_notes import AlterTodaysNotesDialog
from openmolar.qt4gui.dialogs.find_patient_dialog import FindPatientDialog
from openmolar.qt4gui.dialogs.family_manage_dialog import LoadRelativesDialog
from openmolar.qt4gui.dialogs.auto_address_dialog import AutoAddressDialog
from openmolar.qt4gui.dialogs.family_manage_dialog import FamilyManageDialog
from openmolar.qt4gui.dialogs.nhs_forms_config_dialog import NHSFormsConfigDialog
from openmolar.qt4gui.dialogs.advanced_tx_planning_dialog import AdvancedTxPlanningDialog
from openmolar.qt4gui.dialogs.document_dialog import DocumentDialog
from openmolar.qt4gui.dialogs.account_severity_dialog import AccountSeverityDialog
from openmolar.qt4gui.dialogs.daybook_item_dialog import DaybookItemDialog
from openmolar.qt4gui.dialogs.daybook_edit_dialog import DaybookEditDialog
from openmolar.qt4gui.dialogs.course_edit_dialog import CourseEditDialog
from openmolar.qt4gui.dialogs.course_merge_dialog import CourseMergeDialog
from openmolar.qt4gui.dialogs.estimate_edit_dialog import EstimateEditDialog
from openmolar.qt4gui.dialogs.course_history_options_dialog import CourseHistoryOptionsDialog
from openmolar.qt4gui.dialogs.course_consistency_dialog import CourseConsistencyDialog
from openmolar.qt4gui.dialogs.edit_treatment_dialog import EditTreatmentDialog
from openmolar.qt4gui.dialogs.login_dialog import LoginDialog
from openmolar.qt4gui.dialogs.edit_referral_centres_dialog import EditReferralCentresDialog

__all__ = ['AccountSeverityDialog',
           'AdvancedTxPlanningDialog',
           'AlterTodaysNotesDialog',
           'AssistantSelectDialog',
           'AutoAddressDialog',
           'BPE_Dialog',
           'ChildSmileDialog',
           'ChooseToothDialog',
           'ClinicianSelectDialog',
           'CourseConsistencyDialog',
           'CourseEditDialog',
           'CourseMergeDialog',
           'CourseHistoryOptionsDialog',
           'DaybookItemDialog',
           'DaybookEditDialog',
           'DocumentDialog',
           'DuplicateReceiptDialog',
           'EditTreatmentDialog',
           'EditReferralCentresDialog',
           'EstimateEditDialog',
           'ExamWizard',
           'FamilyManageDialog',
           'FindPatientDialog',
           'HygTreatWizard',
           'LoadRelativesDialog',
           'LoginDialog',
           'MedNotesDialog',
           'NHSFormsConfigDialog',
           'RecallDialog',
           'SaveDiscardCancelDialog',
           ]

if __name__ == "__main__":
    print "All imports suceeded!"
