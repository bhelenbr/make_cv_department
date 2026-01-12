#! /usr/bin/env python3
# import modules
import os,sys,platform,shutil
import pandas as pd
import re
import xlrd
from pathlib import Path
from datetime import date

from make_cv.stringprotect import abbreviate_name_list
from copy_with_timestamp import copy_with_timestamp
from merge_df import merge_and_dedup

source = sys.argv[1]
facultyFolder = sys.argv[2]
df = pd.read_excel(source,skiprows=1,dtype={'ID': str})
destination = Path("Service") / "advisee counts.xlsx"
backup_dir = "make_cv/Backups"
emplid_file = Path("make_cv") / "PersonalData" / "employee_id.txt"

today = date.today()
year = today.year
df["YEAR"] = year

faculty_path = Path(facultyFolder)
if not faculty_path.is_dir():
	print(f"Error: destination '{facultyFolder}' is not a directory")
	sys.exit(2)

os.chdir(faculty_path) # changes directory to Faculty folder

for FacultyName in os.listdir("."):
	if FacultyName.find(",") > -1 and Path(FacultyName).is_dir():
		print(f'Adding Advisor Counts for {FacultyName} ',end='')
		personal_folder = Path(FacultyName) / emplid_file
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
			toAppend = entries[["Advisor Name","Count Distinct Name","YEAR"]]
			filename = Path(FacultyName) / destination

			# ensure parent and backup
			filename.parent.mkdir(parents=True, exist_ok=True)
			backup_path = Path(FacultyName) / Path(backup_dir)
			backup_path.mkdir(parents=True, exist_ok=True)

			if filename.is_file():
				copy_with_timestamp(filename, str(backup_path))
				existing_data = pd.read_excel(filename)
				result = merge_and_dedup(existing_data, toAppend, ignore_cols=[]).sort_values(by=['YEAR'],ascending=[True])
				with pd.ExcelWriter(filename) as writer:
					result.to_excel(writer,index=False)
				print(f'Appended {result.shape[0]-existing_data.shape[0]} entries')
			else:
				with pd.ExcelWriter(filename) as writer:
					toAppend.to_excel(writer,index=False)
				print(f'Created file with {toAppend.shape[0]} entries')
		else:
			print('Not Found')
