#!/usr/bin/env python3

import os
import pandas as pd
import sys
from pathlib import Path
import re

from make_cv.stringprotect import abbreviate_name

# --------- CONFIGURATION ---------
excel_file = sys.argv[1]
faculty_folder = sys.argv[2]   # CHANGE THIS
output_filename = Path("make_cv") / "PersonalData" / "personal_data.txt"
sheet_name = 0  # first sheet
# ---------------------------------

# Load Excel file
df = pd.read_excel(excel_file, sheet_name="Sheet1",dtype={"EMPLID": str, "Scopus": str})

# Clean name fields (important for matching)
df["Faculty"] = (
	(df["FIRST_NAME"].astype(str) +" " +df["LAST_NAME"].astype(str))
	.apply(lambda x: abbreviate_name(x,first_initial_only=True).lower())
)

df["EMPLID"] = df["EMPLID"].str.strip()
df["Scopus"] = df["Scopus"].str.strip()
df.fillna("", inplace=True)

# Loop through employees
faculty_path = Path(faculty_folder)
if not faculty_path.is_dir():
	print(f"Error: destination '{faculty_folder}' is not a directory")
	sys.exit(2)

for faculty_dir in faculty_path.iterdir():
	if faculty_dir.is_dir() and faculty_dir.name.find(",") > -1:
		FacultyName = faculty_dir.name
		print(f"Writing ID for {FacultyName}")
		name = abbreviate_name(FacultyName,first_initial_only=True).lower()
		entries=df[df["Faculty"]==name]
		if len(entries) == 1:
			# Use raw string values from the sheet (avoid int() conversion which may fail on blanks)
			employee_id = entries["EMPLID"].iloc[0].strip()
			scopus_id = entries["Scopus"].iloc[0].strip()

			output_path = faculty_dir / output_filename

			if output_path.exists():
				print(f"Found existing {output_path}")
				text = output_path.read_text()
				if text.find("employeeid") >= 0:
					# remove existing employeeid line
					text = re.sub(r'(?im)^[ \t]*employeeid[ \t]*=[ \t]*.*$', '', text)
				if text.find("scopusid") >= 0:
					# remove existing scopusid line
					text = re.sub(r'(?im)^[ \t]*scopusid[ \t]*=[ \t]*.*$', '', text)
				# remove multiple blank lines
				text = re.sub(r'\n{2,}', '\n', text)
				text = text.rstrip()
				# append new lines
				text = text +f"\nemployeeid = {employee_id}\n"
				text = text +f"scopusid = {scopus_id}\n"
				output_path.write_text(text)
				print(f"Updated {output_path} with employeeid={employee_id} scopusid={scopus_id}")
				continue
			else:
				print(f"Error no file found at {output_path}")
