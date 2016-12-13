#! /bin/bash

# this script is used to generate new sql scripts for generation of an openmolar
# database.

# step one - dump the bare bones table layout
mysqldump -u openmolar_user -ppassword --no-data --skip-triggers openmolar_demo > ../src/openmolar/resources/schema.sql 

# step two - dump any triggers (these are not handled well my python MySQLdb)
mysqldump -u openmolar_user -ppassword --no-create-info --no-data --no-create-info --triggers openmolar_demo > ../src/openmolar/resources/triggers.sql 

# step three  - minimal data required for openmolar to run.
mysqldump -u openmolar_user -ppassword --no-create-info --skip-triggers openmolar_demo opid cbcodes settings medications > ../src/openmolar/resources/minimal_data.sql 

# step three 
mysqldump -u openmolar_user -ppassword --no-create-info --skip-triggers openmolar_demo clinical_memos feescales formatted_notes forum forum_important forum_parents forumread new_patients patient_dates patient_money standard_letters static_chart > ../src/openmolar/resources/demo_data.sql 
