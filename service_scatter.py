#! /usr/bin/env python3

import os
import sys
import shutil
import pandas as pd
import argparse
from pathlib import Path

from make_cv.stringprotect import abbreviate_name
from make_cv.copy_with_timestamp import copy_with_timestamp
from merge_df import merge_and_dedup


# ---------------- CLI ----------------
parser = argparse.ArgumentParser(
	description='Scatter department committee data to faculty service files'
)
parser.add_argument('file', help='Excel file to scatter')
parser.add_argument('destination', help='Faculty directory')
parser.add_argument('-y', '--year', type=int, required=True,
					help='Calendar year of data to scatter')

args = parser.parse_args()

facultyFolder = args.destination
source = args.file
year = args.year
backup_dir = "make_cv/Backups"

# ---------------- Load data ----------------
committees = pd.read_excel(source)
committees = committees[committees["Calendar Year"] == year]
committees["Faculty"] = (
	committees["Faculty"]
	.astype(str)
	.apply(lambda x: abbreviate_name(x,first_initial_only=True).lower())
)
committees.fillna(value={"Comments": ""}, inplace=True)

# ---------------- Scatter ----------------
faculty_path = Path(facultyFolder)
if not faculty_path.is_dir():
	print(f"Error: destination '{facultyFolder}' is not a directory")
	sys.exit(2)

for faculty_dir in faculty_path.iterdir():
	if not faculty_dir.is_dir():
		continue
	FacultyName = faculty_dir.name
	if FacultyName.find(",") > -1:
		print(f"Adding service entries to {FacultyName}: ",end="")

		faculty_key = abbreviate_name(FacultyName,first_initial_only=True).lower()
		entries = committees[committees["Faculty"] == faculty_key]
		if entries.shape[0] > 0:
			toAppend = entries.drop(columns=["Faculty", "Department"], errors="ignore")
            
			service_dir = faculty_dir / "Service"            
			filename = service_dir / "service data.xlsx"

			# ---------------- Read existing file ----------------
			if filename.is_file():
				copy_with_timestamp(filename, str(backup_path))
				excelFile = pd.read_excel(filename, sheet_name=None)
				existing_data = excelFile.get("Data", pd.DataFrame())
				existing_data.fillna(value={"Comments": ""}, inplace=True)
				notes = excelFile.get("Notes", pd.DataFrame())
			else:
				existing_data = pd.DataFrame()
				notes = pd.DataFrame()
            
			result = merge_and_dedup([existing_data,toAppend]).sort_values(
				by=["Calendar Year", "Term", "Description"],
				ascending=[True, False, True]
			)
            
			# ---------------- Write ----------------
			with pd.ExcelWriter(filename, engine="openpyxl", mode="w") as writer:
				notes.to_excel(writer, sheet_name="Notes", index=False)
				result.to_excel(writer, sheet_name="Data", index=False)
			print(f'Appended {result.shape[0] -existing_data.shape[0]}')
		else:
			print('No entries')


