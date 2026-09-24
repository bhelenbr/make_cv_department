#! /usr/bin/env python3

# This code will be used to transfer individual professor evaluation data to their respective data files
# from the master evaluation spreadsheet

# import modules
import pandas as pd
import os
import platform
import sys
from pathlib import Path
import openpyxl
import re

from make_cv.stringprotect import abbreviate_name
from make_cv.copy_with_timestamp import copy_with_timestamp
from merge_df import merge_and_dedup

facultyFolder = sys.argv[2]
source = sys.argv[1]
backup_dir = "make_cv/Backups"
emplid_file = Path("make_cv") / "PersonalData" / "personal_data.txt"


# --- Load data ---
df = pd.read_excel(source)
df.fillna(value={"Staff": "", "Deposit": ""}, inplace=True)
df["Deposit"] = (df["Deposit"] == "Deposit").astype(int)
df["Staff"] = df["Staff"].apply(
	lambda x: abbreviate_name(x.split("-")[0].strip(),first_initial_only=True).lower() if "-" in x else abbreviate_name(x,first_initial_only=True).lower()
)
df["Year"] = df["Date of Visit"].astype(str).str[:4].astype(int)

# --- Aggregate ---
table = (
	df.groupby(["Staff ID", "Year"])
	  .agg(
		  Visits=("Person Last", "count"),
		  Deposits=("Deposit", "sum")
	  )
	  .reset_index()
)

# --- Write per faculty ---
faculty_path = Path(facultyFolder)
if not faculty_path.is_dir():
	print(f"Error: destination '{facultyFolder}' is not a directory")
	sys.exit(2)

for faculty_dir in faculty_path.iterdir():
	if not faculty_dir.is_dir():
		continue
	FacultyName = faculty_dir.name
	if FacultyName.find(",") > -1:
		personal_file = faculty_dir / emplid_file
		if not personal_file.is_file():
			print(f"Skipping {FacultyName} (missing personal_data.txt)")
			continue
		try:
			personal_file_text = personal_file.read_text() 
			employee_id = int(re.search(r'employeeid[ \t]*=[ \t]*(\d+)', personal_file_text, re.IGNORECASE).group(1))
		except Exception:
			print(' (invalid employee_id)')
			continue

		print(f'Adding prospective visit data for {FacultyName}: ', end="")
		entries = table[table['Staff ID'].astype(int) == employee_id]
		if entries.shape[0] > 0:

			filename = faculty_dir / "Service" / "prospective visit data.xlsx"
			if filename.is_file():
				backup_path = faculty_dir / backup_dir
				copy_with_timestamp(filename, str(backup_path))
				existing = pd.read_excel(filename)
				# Visits/Deposits are running totals: a re-run replaces that year's row
				# with the new counts instead of adding a second row for the same year
				result = merge_and_dedup([entries, existing], ignore_cols=["Visits", "Deposits"]).sort_values(by=["Year"])
				print(f'Appended {result.shape[0] - existing.shape[0]}')
			else:
				result = entries.sort_values(by=["Year"])
				print(f'Wrote {result.shape[0]} entries')

			with pd.ExcelWriter(filename, engine="openpyxl", mode="w") as writer:
				result.to_excel(writer, index=False)
		else:
			print('No entries')
