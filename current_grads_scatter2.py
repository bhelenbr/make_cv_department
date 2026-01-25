#! /usr/bin/env python3

import os,sys,platform,shutil
import pandas as pd
import numpy as np
import datetime
import xlsxwriter
from datetime import date
from pathlib import Path

from make_cv.copy_with_timestamp import copy_with_timestamp

pd.options.mode.chained_assignment = None  # default='warn'

# This reads the current student data then rewrites with updated notes
# You may have to install pandas: pip3 install pandas
# Python code to scatter current student data
# First argument is file to scatter

source = sys.argv[1]
file_destination = sys.argv[2]
emplid_file = Path("make_cv") / "PersonalData" / "employee_id.txt"
backup_dir = Path("make_cv") / "Backups"

df = pd.read_excel(source,skiprows=1,dtype={'ID': str})
df = df[df["Career"]=="GRAD"]

df.drop(columns=['ID','Email','Career','Advisor','Email.1'], axis=1, inplace=True)
df = df.fillna("")
destination = "Scholarship" +os.sep +"current student data.xlsx"
faculty_path = Path(file_destination)
if not faculty_path.is_dir():
	print(f"Error: destination '{file_destination}' is not a directory")
	sys.exit(2)

for faculty_dir in faculty_path.iterdir():
	if not faculty_dir.is_dir():
		continue
	FacultyName = faculty_dir.name
	if FacultyName.find(",") > -1:
		print(f'Adding graduate advisees for {FacultyName}: ', end="")

		# Get employee id
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



		entries = df.loc[df['Advisor ID'].astype(int) == employee_id]
		if entries.shape[0] > 0:
			entries["Student Name"] = entries["Last"] + ", " + entries["First Name"]
			entries["Current Program"] = entries["Acad Plan"]
			entries["Start Date"] = pd.to_datetime(str(date.today()))
			entries = entries.drop(columns=["Last","First Name","Acad Plan","Advisor ID"])
			entries.sort_values(by=['Current Program','Start Date'],inplace=True)
			

			filename = faculty_dir / destination
			if Path(filename).is_file():
				backup_path = faculty_dir / backup_dir
				copy_with_timestamp(filename, str(backup_path))
			with pd.ExcelWriter(filename,date_format='YYYY-MM-DD', datetime_format='YY-MM-DD') as writer:
				entries.to_excel(writer,sheet_name='Data',index=False)
			print(f'{entries.shape[0]} entries')
		else:
			print('No entries')
