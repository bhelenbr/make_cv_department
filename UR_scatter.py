#! /usr/bin/env python3

# Python code to scatter Undergraduate research data to faculty folders
# argument is file to scatter

# import modules
import os,sys,platform,shutil
import pandas as pd
import re
import xlrd
from pathlib import Path

from make_cv.stringprotect import abbreviate_name
from make_cv.stringprotect import abbreviate_name_list
from copy_with_timestamp import copy_with_timestamp
from merge_df import merge_and_dedup

source = sys.argv[1]
facultyFolder = sys.argv[2]
emplid_file = Path("make_cv") / "PersonalData" / "employee_id.txt"
destination = Path("Service") / "undergraduate research data.xlsx"
backup_dir = Path("make_cv") / "Backups"

df = pd.read_excel(source, skiprows=1, dtype={'Advisor ID': str})
df.columns = [c.strip() for c in df.columns]
classnum = df["Class"].apply(lambda x: int(str(x)[-3:]))
df = df[classnum < 499]
df = df[df['Title'] != 'Aircraft Design I']
df = df[df['Title'] != 'Professional Experience']
df['Calendar Year'] = df['Term'].apply(lambda x: int(x[-4:]))
df['Term'] = df['Term'].apply(lambda x: x[:-5])
df['Program Type'] = df['Program Type'].apply(lambda x: re.sub("Independent Study","Ind. Proj.",re.sub("Research","Und. Res.",x)))
df = df.rename(columns={"Student Name": "Students"})
df['Students'] = df['Students'].apply(lambda x: abbreviate_name_list(x))

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
		print(f'Adding undergraduate research classes for {FacultyName} ',end='')
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
		entries = df.loc[df["Advisor ID"].astype(int) == employee_id]
		if entries.shape[0] > 0:
			toAppend = entries[['Students','Title','Program Type','Term','Calendar Year']]
			filename = faculty_dir / destination

			# ensure destination folder exists
			filename.parent.mkdir(parents=True, exist_ok=True)

			# ensure backup path exists
			backup_path = faculty_dir / Path(backup_dir)
			backup_path.mkdir(parents=True, exist_ok=True)

			if filename.is_file():
				copy_with_timestamp(filename, str(backup_path))
				existing_data = pd.read_excel(filename, sheet_name='Data')
				result = merge_and_dedup(existing_data, toAppend, ignore_cols=['Title']).sort_values(by=['Calendar Year','Term','Program Type','Students'], ascending=[True,False,True,True])
				with pd.ExcelWriter(filename) as writer:
					result.to_excel(writer, sheet_name='Data', index=False)
				print(f'Appended {result.shape[0] - existing_data.shape[0]}')
			else:
				with pd.ExcelWriter(filename) as writer:
					toAppend.to_excel(writer, sheet_name='Data', index=False)
				print(f'New {toAppend.shape[0]}')
		else:
			print(f'No entries')
