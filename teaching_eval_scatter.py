#! /usr/bin/env python3

# This code will be used to transfer individual professor evaluation data to their respective data files
# from the master evaluation spreadsheet

# import modules
import pandas as pd
import os
import platform
import sys
from pathlib import Path

from copy_with_timestamp import copy_with_timestamp

faculty_dir = sys.argv[2]
source_file = sys.argv[1]
emplid_file = "make_cv" +os.sep +"PersonalData" +os.sep +"employee_id.txt"
backup_dir = "make_cv/Backups"

df = pd.read_excel(source_file,skiprows=1)
new_columns = [ "STRM","term","school","course","course_num","course_section","course_title","INSTR_NA","ID","count_evals","enrollment","Particip","question","a1","a1_pct","a2","a2_pct","a3","a3_pct","a4","a4_pct","a5","a5_pct","na","na_pct","Calculated Mean","Question","combined_course_num"]
df.columns = new_columns
df["Weighted Average"] = df["count_evals"]*df["Calculated Mean"]
df["combined_course_num"] = df["combined_course_num"].fillna(df["course_num"])

os.chdir(faculty_dir) # where files need to go

for FacultyName in os.listdir("."):
	if FacultyName.find(",") > -1:
		print(f'Updating teaching evaluations for {FacultyName} ',end='')
		personal_folder = FacultyName +os.sep +emplid_file
		with open(personal_folder, "r") as f:
			employee_id = int(f.read().strip())
			
		# Get entries for this faculty
		entries=df.loc[df["ID"].astype(int) == employee_id]
		if entries.shape[0] > 0:
			destination = FacultyName + "/Teaching/" + "/teaching evaluation data.xlsx"
			if Path(destination).is_file():
				copy_with_timestamp(destination,FacultyName+os.sep+backup_dir)
			with pd.ExcelWriter(FacultyName + "/Teaching/" + "/teaching evaluation data.xlsx") as writer:
					entries.to_excel(writer,sheet_name='Data',index=False)
		print(f'added {entries.shape[0]} entries')
