#! /usr/bin/env python3
# import modules
import os,sys,platform,shutil
import pandas as pd
import re
import xlrd
from pathlib import Path
from datetime import date

from make_cv.stringprotect import abbreviate_name
from copy_with_timestamp import copy_with_timestamp

source = sys.argv[1]
facultyFolder = sys.argv[2]
destination = Path("Proposals & Grants") / "expenditures.xlsx"
emplid_file = Path("make_cv") / "PersonalData" / "employee_id.txt"
backup_dir = "make_cv/Backups"

df = pd.read_excel(source,skiprows=1,dtype={'EMPLID': str})
df["Name"] = (
	df["Name"]
	.astype(str)
	.apply(lambda x: abbreviate_name(x,first_initial_only=True).lower())
)
df.drop(['F(Fiscal Year) or C(Calendar)','Start Term','End Term','Year1'], axis=1,inplace=True)

faculty_path = Path(facultyFolder)
if not faculty_path.is_dir():
	print(f"Error: destination '{facultyFolder}' is not a directory")
	sys.exit(2)

os.chdir(faculty_path) # changes directory to Faculty folder

for FacultyName in os.listdir("."):
	if not Path(FacultyName).is_dir():
		continue
	if FacultyName.find(",") > -1:
		print(f'Updating expenditures for {FacultyName} ',end='')
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
		entries=df.loc[df["EMPLID"].astype(int) == employee_id]
		entries = entries.drop(columns = ["EMPLID"])
		if entries.shape[0] > 0:
			filename = Path(FacultyName) / destination
			# ensure parent exists
			filename.parent.mkdir(parents=True, exist_ok=True)

			# ensure backup dir exists
			backup_path = Path(FacultyName) / Path(backup_dir)
			backup_path.mkdir(parents=True, exist_ok=True)

			if filename.is_file():
				copy_with_timestamp(filename, str(backup_path))
				excelFile = pd.read_excel(filename)
				existing_data = excelFile
				result = pd.concat([excelFile, entries],ignore_index=True)
				result = result.drop_duplicates()
				result.sort_values(by=['Year'],ascending=[True],inplace=True)
				with pd.ExcelWriter(filename) as writer:
					result.to_excel(writer,index=False)
				appended = max(0, result.shape[0] - existing_data.shape[0])
				print(f'Appended {appended}')
			else:
				with pd.ExcelWriter(filename) as writer:
					entries.to_excel(writer,index=False)
				print(f'Added {entries.shape[0]}')
		else:
			print('No entries')
