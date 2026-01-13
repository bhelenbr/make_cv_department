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

from make_cv.stringprotect import abbreviate_name
from copy_with_timestamp import copy_with_timestamp
from merge_df import merge_and_dedup

import sys
import os
from pathlib import Path
import pandas as pd

facultyFolder = sys.argv[2]
source = sys.argv[1]
backup_dir = "make_cv/Backups"

# --- Load data ---
df = pd.read_excel(source)
df.fillna(value={"Staff": "", "Deposit": ""}, inplace=True)
df["Deposit"] = (df["Deposit"] == "Deposit").astype(int)
df["Staff"] = df["Staff"].apply(
	lambda x: abbreviate_name(x.split("-")[0].strip()) if "-" in x else abbreviate_name(x,first_initial_only=True)
)
df["Year"] = df["Date of Visit"].astype(str).str[:4].astype(int)

# --- Aggregate ---
table = (
	df.groupby(["Staff", "Year"])
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
		print(f'Adding prospective visit data for {FacultyName}: ', end="")
		faculty_key = abbreviate_name(FacultyName, first_initial_only=True).lower()
		entries = table[table['Staff'] == faculty_key]
		if entries.shape[0] > 0:

			filename = faculty_dir / "Service" / "prospective visit data.xlsx"

			filename.parent.mkdir(parents=True, exist_ok=True)
			backup_path = faculty_dir / Path(backup_dir)
			backup_path.mkdir(parents=True, exist_ok=True)

			if filename.is_file():
				copy_with_timestamp(filename, str(backup_path))
				existing = pd.read_excel(filename)
				result = merge_and_dedup(existing, entries, ignore_cols=[]).sort_values(by=["Year"])
			else:
				result = entries.sort_values(by=["Year"])

			with pd.ExcelWriter(filename, engine="openpyxl", mode="w") as writer:
				result.to_excel(writer, index=False)
			print(f'Appended {result.shape[0] - existing.shape[0]}')
		else:
			print('No entries')
	
