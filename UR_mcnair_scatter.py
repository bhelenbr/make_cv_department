#! /usr/bin/env python3

import os
import sys
import pandas as pd
import argparse
from pathlib import Path

from make_cv.stringprotect import abbreviate_name
from copy_with_timestamp import copy_with_timestamp
from merge_df import merge_and_dedup

import re

# ---------------- CLI ----------------
parser = argparse.ArgumentParser(
	description='Scatter McNair mentoring data to faculty undergraduate research files'
)
parser.add_argument('file', help='Excel file to scatter')
parser.add_argument('destination', help='Departments root directory')
parser.add_argument('-y', '--year', type=int, required=True,
					help='Calendar year of data to scatter')

args = parser.parse_args()

facultyFolder = args.destination
source = args.file
year = args.year
backup_dir = "make_cv/Backups"

# ---------------- Load data ----------------
mcnair = pd.read_excel(source, sheet_name='Sheet1')

# Clean column names
mcnair.columns = [col.strip() for col in mcnair.columns]

# Filter by year
required_cols = {'YEAR', 'Faculty', 'Last Name', 'First Name', 'Term'}
missing = required_cols - set(mcnair.columns)
if missing:
	print(f"Error: input file is missing required columns: {', '.join(sorted(missing))}")
	sys.exit(2)

mcnair = mcnair[mcnair['YEAR'] == year]

# Clean and abbreviate mentor names
def clean_mentor_name(mentor):
	if pd.isna(mentor):
		return ''
	mentor = str(mentor).strip()
	# Remove titles
	mentor = re.sub(r'(Dr\.|Prof\.|Mr\.|Ms\.|Mrs\.)', '', mentor).strip()
	mentor = abbreviate_name(mentor, first_initial_only=True).lower()
	return mentor

mcnair['mentor_key'] = mcnair['Faculty'].apply(clean_mentor_name)

# ---------------- Scatter ----------------
faculty_path = Path(facultyFolder)
if not faculty_path.is_dir():
	print(f"Error: destination '{facultyFolder}' is not a directory")
	sys.exit(2)

for faculty_dir in faculty_path.iterdir():
	if not faculty_dir.is_dir():
		continue
	FacultyName = faculty_dir.name
	# only consider directories named like 'Last, First'
	if FacultyName.find(",") > -1:
		print(f'Adding McNair entries for {FacultyName} ',end='')
		faculty_key = abbreviate_name(FacultyName, first_initial_only=True).lower()
		entries = mcnair[mcnair['mentor_key'] == faculty_key]

		if entries.shape[0] > 0:
			toAppend = pd.DataFrame([
				{
					'Students': f"{row['Last Name'].strip()}, {row['First Name'].strip()}",
					'Title': 'McNair Scholars Program',
					'Program Type': 'McNair',
					'Term': row['Term'],
					'Calendar Year': year
				}
				for _, row in entries.iterrows()
			])

			service_dir = faculty_dir / "Service"
			filename = service_dir / "undergraduate research data.xlsx"

			# ensure parent and backup
			filename.parent.mkdir(parents=True, exist_ok=True)
			backup_path = faculty_dir / Path(backup_dir)
			backup_path.mkdir(parents=True, exist_ok=True)

			# ---------------- Read existing file ----------------
			if filename.is_file():
				copy_with_timestamp(filename, str(backup_path))
				excelFile = pd.read_excel(filename, sheet_name=None)
				existing_data = excelFile.get("Data", pd.DataFrame())
				notes = excelFile.get("Notes", pd.DataFrame())
			else:
				existing_data = pd.DataFrame()
				notes = pd.DataFrame()

			result = merge_and_dedup([existing_data,toAppend],ignore_cols=['Title']).sort_values(
				by=["Calendar Year", "Term", "Program Type"],
				ascending=[True, False, True]
			)
			# ---------------- Write ----------------
			with pd.ExcelWriter(filename, engine="openpyxl", mode="w") as writer:
				notes.to_excel(writer, sheet_name="Notes", index=False)
				result.to_excel(writer, sheet_name="Data", index=False)
			print(f'Appended {result.shape[0] - existing_data.shape[0]}')	
		else:
			print('No entries')