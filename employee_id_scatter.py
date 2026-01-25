#!/usr/bin/env python3

import os
import pandas as pd
import sys
from pathlib import Path

from make_cv.stringprotect import abbreviate_name

# --------- CONFIGURATION ---------
excel_file = sys.argv[1]
faculty_folder = sys.argv[2]   # CHANGE THIS
output_filename = Path("make_cv") / "PersonalData" / "employee_id.txt"
sheet_name = 0  # first sheet
# ---------------------------------

# Load Excel file
df = pd.read_excel(excel_file, sheet_name="Sheet1",dtype={"EMPLID": str})

# Clean name fields (important for matching)
df["Faculty"] = (
	(df["FIRST_NAME"].astype(str) +" " +df["LAST_NAME"].astype(str))
	.apply(lambda x: abbreviate_name(x,first_initial_only=True).lower())
)
df["EMPLID"] = df["EMPLID"].str.strip()

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
			employee_id = int(entries["EMPLID"].iloc[0])
			output_path = faculty_dir / output_filename
			with open(output_path, "w") as f:
				f.write(f"{employee_id}")
		else:
			print(f"No unique match {len(entries)} for {FacultyName}")
