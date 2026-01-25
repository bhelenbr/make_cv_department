#! /usr/bin/env python3

import os
import sys
import pandas as pd
import argparse
import re
from pathlib import Path

from make_cv.stringprotect import abbreviate_name
from make_cv.copy_with_timestamp import copy_with_timestamp
from merge_df import merge_and_dedup


# ---------------- CLI ----------------
parser = argparse.ArgumentParser(
	description='Scatter honors capstone mentoring data to faculty undergraduate research files'
)
parser.add_argument('file', help='Excel file to scatter')
parser.add_argument('destination', help='Departments root directory')
parser.add_argument('-y', '--year', type=int, required=True,
					help='Calendar year of data to scatter')

args = parser.parse_args()

facultyFolder = args.destination
source = args.file
year = args.year
backup_dir = Path("make_cv") / "Backups"

# ---------------- Load data ----------------
capstones = pd.read_excel(source, sheet_name='Grades')

# Clean column names
capstones.columns = [col.strip() for col in capstones.columns]

# Validate required columns
required_cols = {'Honors Mentor', 'Last name', 'First name', 'Title of Your Capstone', 'Grad'}
missing = required_cols - set(capstones.columns)
if missing:
	print(f"Error: input file is missing required columns: {', '.join(sorted(missing))}")
	sys.exit(2)

# Clean and abbreviate mentor names
def clean_mentor_name(mentor):
	if pd.isna(mentor):
		return ''
	mentor = str(mentor).strip()
	# Remove email in parentheses
	mentor = re.sub(r'\(.*?\)', '', mentor).strip()
	# Remove titles
	mentor = re.sub(r'(Dr\.|Prof\.|Mr\.|Ms\.|Mrs\.)', '', mentor).strip()
	mentor = abbreviate_name(mentor, first_initial_only=True).lower()
	return mentor

capstones['mentor_key'] = capstones['Honors Mentor'].apply(clean_mentor_name)

# Function to map Grad to Term
def map_grad_to_term(grad):
	if pd.isna(grad):
		return 'Spring'  # Default
	grad_str = str(grad).lower()
	months = ['jan', 'feb', 'mar', 'apr']
	if any(month in grad_str for month in months) or 'spring' in grad_str:
		return 'Spring'
	elif 'may' in grad_str or 'jun' in grad_str or 'jul' in grad_str or 'aug' in grad_str or 'summer' in grad_str:
		return 'Summer'
	elif 'sep' in grad_str or 'oct' in grad_str or 'nov' in grad_str or 'dec' in grad_str or 'fall' in grad_str:
		return 'Fall'
	else:
		return 'Spring'  # Default for non-month notes like "Asked"

capstones['Term'] = capstones['Grad'].apply(map_grad_to_term)

# Filter for completed capstones (all signatures Yes and title present)
# capstones = capstones[
#	 (capstones['Title of Your Capstone'].notna()) &
#	 (capstones['CASPER ONLY SIGNED BY REVIEWER'] == 'Yes') &
#	 (capstones['CASPER ONLY SIGNED BY MENTOR'] == 'Yes') &
#	 (capstones['CASPER ONLY SIGNED BY DIRECTOR'] == 'Yes')
# ]

# Walk the departments root to find faculty Service folders
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
		print(f'Adding honors theses for {FacultyName} ',end='')
		faculty_key = abbreviate_name(FacultyName, first_initial_only=True).lower()
		entries = capstones[capstones['mentor_key'] == faculty_key]

		if entries.shape[0] > 0:
			toAppend = pd.DataFrame([
				{
					'Students': f"{row['Last name'].strip()}, {row['First name'].strip()}",
					'Title': row['Title of Your Capstone'],
					'Program Type': 'Honors Capstone',
					'Term': row['Term'],
					'Calendar Year': year
				}
				for _, row in entries.iterrows()
			])

			service_dir = faculty_dir / "Service"           
			filename = service_dir / "undergraduate research data.xlsx"

			# ---------------- Read existing file ----------------
			if filename.is_file():
				backup_path = faculty_dir / backup_dir
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
			