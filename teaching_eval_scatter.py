#! /usr/bin/env python3

# This code will be used to transfer individual professor evaluation data to their respective data files
# from the master evaluation spreadsheet

# import modules
import pandas as pd
import os
import platform
import sys
import re
from pathlib import Path

from make_cv.copy_with_timestamp import copy_with_timestamp
from merge_df import merge_and_dedup

facultyFolder = sys.argv[2]
source = sys.argv[1]
emplid_file = Path("make_cv") / "PersonalData" / "personal_data.txt"
backup_dir = Path("make_cv") / "Backups"

# "Term", "Description", "School", "Descr2", "Catalog", "Section", "Component", "Mode", "Descr 3", "LN,FN", "ID", "Ct Evals", "Tot Enrl", "Participant", "Number", "A1 count", "A1 percent", "A2 count", "A2 percent", "A3 count", "A3 percent", "A4 count", "A4 percent", "A5 count", "A5 percent", "NA count", "NA percent", "Q Mean", "Question", "Class Nbr", "Comb Sects ID", "Descr"
df = pd.read_excel(source, skiprows=1, engine="xlrd")
df.drop(columns=['A1 percent','A2 percent','A3 percent','A4 percent','A5 percent','NA percent'], axis=1, inplace=True)

try:
	# new_columns = [ "STRM","term","school","course","course_num","course_section","component","course_title","INSTR_NA","ID","count_evals","enrollment","Particip","question","a1","a1_pct","a2","a2_pct","a3","a3_pct","a4","a4_pct","a5","a5_pct","na","na_pct","Calculated Mean","Question","combined_course_num"]
	#df.columns = new_columns
	new_column_names = {"Term": "STRM", "Description": "term", "Descr2": "course_sec", "Catalog": "course_num", "Section": "course_section", "Component": "component", "Mode": "mode", "Descr 3": "course_title", "LN,FN": "INSTR_NA", "Ct Evals":"count_evals", "Tot Enrl": "enrollment", "Participant": "Particip", "Number":"question", "A1 count": "a1", "A2 count": "a2", "A3 count":"a3", "A4 count":"a4", "A5 count":"a5", "NA count": "na", "Q Mean": "Calculated Mean", "Question": "question_text", "Descr": "combined_course_num"}
	df.rename(columns=new_column_names, inplace=True)
except Exception:
	print("Error: unexpected columns in source file; column assignment failed")
	sys.exit(2)
df["Weighted Average"] = df["count_evals"]*df["Calculated Mean"]
df["combined_course_num"] = df["combined_course_num"].fillna(df["course_num"])
def _normalize_combined_course_num(val):
	parts = [p.strip() for p in val.split('/')]
	suffixes = []
	for p in parts:
		m = re.search(r'-(.+)$', p)
		if m:
			suffixes.append(m.group(1))
	if len(suffixes) > 1 and len(set(suffixes)) > 1:
		print(f"Warning: course suffixes don't match in '{val}': {suffixes}")

	s = re.sub(r'-[^/]+','', val)
	return s

df["combined_course_num"] = df["combined_course_num"].apply(_normalize_combined_course_num)  # Normalize whitespace and suffixes

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
		personal_file = faculty_dir / emplid_file
		if not personal_file.is_file():
			print(' (missing personal_data.txt)')
			continue
		try:
			personal_file_text = personal_file.read_text() 
			employee_id = int(re.search(r'employeeid[ \t]*=[ \t]*(\d+)', personal_file_text, re.IGNORECASE).group(1))
		except Exception:
			print(' (invalid employee_id)')
			continue
            
		# Get entries for this faculty
		entries=df.loc[df["ID"].astype(int) == employee_id]
		if entries.shape[0] > 0:
			destination = faculty_dir / "Teaching" / "teaching evaluation data.xlsx"

			if destination.is_file():
				backup_path = faculty_dir / backup_dir
				copy_with_timestamp(destination, str(backup_path))
				existing_data = pd.read_excel(destination, sheet_name="Data")
				result = merge_and_dedup([entries, existing_data], keep_only_first_cols=True)
				with pd.ExcelWriter(destination, engine="openpyxl", mode="w") as writer:
					result.to_excel(writer, sheet_name="Data", index=False)
				print(f'Appended {result.shape[0] - existing_data.shape[0]} entries')
			else:
				with pd.ExcelWriter(destination, engine="openpyxl", mode="w") as writer:
					entries.to_excel(writer, sheet_name="Data", index=False)
				print(f'New {entries.shape[0]} entries')
