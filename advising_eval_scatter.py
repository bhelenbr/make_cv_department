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
backup_dir = "make_cv/Backups"

df = pd.read_excel(source,skiprows=1,dtype={'ID': str})

faculty_path = Path(facultyFolder)
if not faculty_path.is_dir():
	print(f"Error: destination '{facultyFolder}' is not a directory")
	sys.exit(2)

count = 1
for faculty_dir in faculty_path.iterdir():
	if not faculty_dir.is_dir():
		continue
	FacultyName = faculty_dir.name
	if FacultyName.find(",") > -1:
		print(f'Adding advising evals for {FacultyName}: ', end="")
		# Get employee id
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
		entries = df.loc[df['ID'].astype(int) == employee_id]
		if entries.shape[0] > 0:
			filename = faculty_dir / "Service" / "advising evaluation data.xlsx"

			if filename.is_file():
				backup_path = faculty_dir / backup_dir
				copy_with_timestamp(filename, str(backup_path))
				existing_data = pd.read_excel(filename,dtype={'ID': str})
				result = merge_and_dedup([existing_data, entries]).sort_values(by=['Term','Number'],ascending=[True,True])			
				with pd.ExcelWriter(filename) as writer:
					result.to_excel(writer,index=False)
				print(f'Appended {result.shape[0] -existing_data.shape[0]}')
			else:
				with pd.ExcelWriter(filename) as writer:
					entries.to_excel(writer,index=False)
				print(f'Added {entries.shape[0]}')
		else:
			print('No new entries')