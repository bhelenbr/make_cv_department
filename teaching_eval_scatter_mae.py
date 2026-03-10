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
from make_cv.stringprotect import abbreviate_name
from make_cv.copy_with_timestamp import copy_with_timestamp
from merge_df import merge_and_dedup

facultyFolder = sys.argv[2]
source = sys.argv[1]
emplid_file = Path("make_cv") / "PersonalData" / "personal_data.txt"
backup_dir = Path("make_cv") / "Backups"


df = pd.read_excel(source)

# Teaching evaluation data has the following columns:
# "Term", "Description", "School", "Descr2", "Catalog", "Section", "Component", "Mode", "Descr 3", "LN,FN", "ID", "Ct Evals", "Tot Enrl", "Participant", "Number", "A1 count", "A1 percent", "A2 count", "A2 percent", "A3 count", "A3 percent", "A4 count", "A4 percent", "A5 count", "A5 percent", "NA count", "NA percent", "Q Mean", "Question", "Class Nbr", "Comb Sects ID", "Descr"
# df.drop(columns=['School','A1 percent','A2 percent','A3 percent','A4 percent','A5 percent','NA percent',"A1 count", "A2 count", "A3 count", "A4 count", "A5 count", "NA count"], axis=1, inplace=True)
# new_column_names = {"Term": "STRM", "Description": "term", "Descr2": "num_sec", "Catalog": "course_num", "Section": "course_section", "Component": "component", "Mode": "mode", "Descr 3": "course_title", "LN,FN": "INSTR_NA", "Ct Evals":"count", "Tot Enrl": "enrollment", "Participant": "role", "Number":"question", "Q Mean": "mean", "Question": "question_text", "Descr": "combined_num_sec"}

# CU_FAR_ALL_CRSES has the following columns:
# Term	Term Description	School	Course and Session Description	Subject	Catalog	Section	Component	Class Description	Instructor ID	Instructor Name	Role	Mode	Comb Sects ID	Ct Evals	Tot Enrl	Participant	Number	A1 count	A2 count	A3 count	A4 count	A5 count	NA count	NA percent	Q Mean	Question	Comb Sects ID	Descr
if not 'course_num' in df.columns:
	df["course_num"] = df['Subject'].str.strip() + df['Catalog'].str.strip()
df["num_sec"] = df['course_num'] + "-" + df['Section']

for col in ['Course and Session Description','Subject','Catalog','A1 count','A2 count','A3 count','A4 count','A5 count','NA count','Comb Sects ID','School','Participant']:
	if col in df.columns:
		df.drop(columns=[col], axis=1, inplace=True)
new_column_names = {"Term": "STRM", "Term Description": "term", "Section": "course_section", "Component": "component", "Mode": "mode", "Class Description": "course_title", "Instructor ID": "ID", "Instructor Name": "INSTR_NA", "Ct Evals":"count", "Total Enrollment": "enrollment", "Role": "role", "Question Number":"question", "Q Mean": "mean", "Question": "question_text", "Combined Sections Descr": "combined_num_sec"}

if not 'Component' in df.columns:
	df['Component'] = 'LEC'

if not 'Mode' in df.columns:
	df['Mode'] = 'P'

if not 'Role' in df.columns:
	df['Role'] = 'PI'


try:
	df.rename(columns=new_column_names, inplace=True)
except Exception:
	print("Error: unexpected columns in source file; column assignment failed")
	sys.exit(2)

df["combined_num_sec"] = df["combined_num_sec"].fillna(df["num_sec"])
df["combined_course_num"] = df["combined_num_sec"].apply(lambda x: re.sub(r'-[^/]+','', x))  # Normalize whitespace and suffixes
df.drop(columns=['question_text','num_sec'], inplace=True)
df['INSTR_NA'] = df['INSTR_NA'].fillna('')
df['INSTR_NA'] = df['INSTR_NA'].apply(lambda x : abbreviate_name(x,first_initial_only=True))

# Remove any rows where enrollment is zero or missing
df = df[df['enrollment'].fillna(0).astype(int) != 0]

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
		abbrv = abbreviate_name(FacultyName,first_initial_only=True)
	
		# Get entries for this faculty
		entries=df.loc[df["INSTR_NA"] == abbrv]
		if entries.shape[0] > 0:
			# Pivot so each question becomes its own set of columns (values: count, mean)
			table = entries.pivot_table(index=['STRM', 'term','course_num', 'course_section','combined_course_num','combined_num_sec','course_title','component','mode','role','enrollment'], columns='question',values=['count','mean'], aggfunc='sum')
			# Convert the pivoted MultiIndex columns into flat single-level column names
			# and turn the index levels into regular columns so the output is a normal DataFrame
			table = table.reset_index()
			# Flatten any MultiIndex columns produced by pivot_table
			table.columns = [
				str(col[0]) +'_' +str(col[1]) if isinstance(col[1], int) else str(col[0])
				for col in table.columns
			]
			# Reorder columns to have the index columns first, followed by the pivoted question columns
			new_order = table.columns[:11].tolist()  # Start with the first 10 index columns
			for q in range(1,21):
				new_order.append(f"count_{q}")
				new_order.append(f"mean_{q}")
				# append any remaining columns not covered (safety)
			new_order += [c for c in table.columns if c not in new_order]
			table = table.loc[:, new_order]

			destination = faculty_dir / "Teaching" / "teaching evaluation data.xlsx"
			if destination.is_file():
				backup_path = faculty_dir / backup_dir
				copy_with_timestamp(destination, str(backup_path))
				existing_data = pd.read_excel(destination, sheet_name="Data")
				result = merge_and_dedup([table, existing_data], keep_only_first_cols=True)
				with pd.ExcelWriter(destination, engine="openpyxl", mode="w") as writer:
					result.to_excel(writer, sheet_name="Data", index=False)
				print(f'Appended {result.shape[0] - existing_data.shape[0]} entries')
			else:
				with pd.ExcelWriter(destination, engine="openpyxl", mode="w") as writer:
					table.to_excel(writer, sheet_name="Data", index=False)
				print(f'New {entries.shape[0]} entries')
