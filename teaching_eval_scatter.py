#! /usr/bin/env python3

# This code will be used to transfer individual professor evaluation data to their respective data files
# from the master evaluation spreadsheet

# import modules
import pandas as pd
import os
import platform
import sys
from pathlib import Path

from make_cv.copy_with_timestamp import copy_with_timestamp
from merge_df import merge_and_dedup

facultyFolder = sys.argv[2]
source = sys.argv[1]
emplid_file = Path("make_cv") / "PersonalData" / "employee_id.txt"
backup_dir = Path("make_cv") / "Backups"

df = pd.read_excel(source, skiprows=1)
new_columns = [ "STRM","term","school","course","course_num","course_section","course_title","INSTR_NA","ID","count_evals","enrollment","Particip","question","a1","a1_pct","a2","a2_pct","a3","a3_pct","a4","a4_pct","a5","a5_pct","na","na_pct","Calculated Mean","Question","combined_course_num"]
try:
	df.columns = new_columns
except Exception:
	print("Error: unexpected columns in source file; column assignment failed")
	sys.exit(2)
df["Weighted Average"] = df["count_evals"]*df["Calculated Mean"]
df["combined_course_num"] = df["combined_course_num"].fillna(df["course_num"])

faculty_path = Path(facultyFolder)
if not faculty_path.is_dir():
	print(f"Error: destination '{facultyFolder}' is not a directory")
	sys.exit(2)

for faculty_dir in faculty_path.iterdir():
	if not faculty_dir.is_dir():
		continue
	FacultyName = faculty_dir.name
	# only consider directories named like 'Last, First'
	if FacultyName.find(",") > -1:
		print(f'Updating teaching evaluations for {FacultyName} ',end='')
		personal_folder = faculty_dir / emplid_file
		if not personal_folder.is_file():
			print(' (missing employee_id)')
			continue
		with open(personal_folder, "r") as f:
			try:
				employee_id = int(f.read().strip())
			except Exception:
				print(' (invalid employee_id)')
				continue
            
		# Get entries for this faculty
		entries=df.loc[df["ID"].astype(int) == employee_id]
		if entries.shape[0] > 0:
			destination = faculty_dir / "Teaching" / "teaching evaluation data.xlsx"

			backup_path = faculty_dir / backup_dir
			if destination.is_file():
				copy_with_timestamp(destination, str(backup_path))
				existing_data = pd.read_excel(destination, sheet_name="Data")
				result = merge_and_dedup([existing_data, entries])
				with pd.ExcelWriter(destination, engine="openpyxl", mode="w") as writer:
					result.to_excel(writer, sheet_name="Data", index=False)
				print(f'Appended {result.shape[0] - existing_data.shape[0]} entries')
			else:
				with pd.ExcelWriter(destination, engine="openpyxl", mode="w") as writer:
					entries.to_excel(writer, sheet_name="Data", index=False)
				print(f'New {entries.shape[0]} entries')
