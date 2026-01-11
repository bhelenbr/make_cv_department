#!/usr/bin/env python3

import os
import pandas as pd
import sys
from make_cv.stringprotect import abbreviate_name

# --------- CONFIGURATION ---------
excel_file = sys.argv[1]
faculty_folder = sys.argv[2]   # CHANGE THIS
output_filename = "make_cv" +os.sep +"PersonalData" +os.sep +"employee_id.txt"
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
for FacultyName in os.listdir(faculty_folder):
	if FacultyName[0].isalnum():
		print(f"Writing ID for {FacultyName}")
		name = abbreviate_name(FacultyName,first_initial_only=True).lower();
		entries=df[df["Faculty"]==name]
		if len(entries) == 1:
			employee_id = int(entries["EMPLID"].iloc[0])
			output_path = os.path.join(faculty_folder +os.sep +FacultyName, output_filename)
			with open(output_path, "w") as f:
				f.write(f"{employee_id}")
		else:
			print(f"No unique match {len(entries)} for {FacultyName}")
