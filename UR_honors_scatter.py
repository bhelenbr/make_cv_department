#! /usr/bin/env python3

import os
import sys
import shutil
import pandas as pd
import argparse
from pathlib import Path
from make_cv.stringprotect import abbreviate_name
from copy_with_timestamp import copy_with_timestamp

import re

# ---------------- CLI ----------------
parser = argparse.ArgumentParser(
	description='Scatter honors capstone mentoring data to faculty undergraduate research files'
)
parser.add_argument('file', help='Excel file to scatter')
parser.add_argument('destination', help='Departments root directory')
parser.add_argument('-y', '--year', type=int, required=True,
					help='Calendar year of data to scatter')

args = parser.parse_args()

departments_root = args.destination
source = args.file
year = args.year
backup_dir = "make_cv/Backups"

# ---------------- Load data ----------------
capstones = pd.read_excel(source, sheet_name='Grades')

# Clean column names
capstones.columns = [col.strip() for col in capstones.columns]

# Clean and abbreviate mentor names
def clean_mentor_name(mentor):
	if pd.isna(mentor):
		return ''
	mentor = str(mentor).strip()
	# Remove email in parentheses
	mentor = re.sub(r'\(.*?\)', '', mentor).strip()
	# Remove titles
	mentor = re.sub(r'(Dr\.|Prof\.|Mr\.|Ms\.|Mrs\.)', '', mentor).strip()
	return mentor

capstones['Honors Mentor Clean'] = capstones['Honors Mentor'].apply(clean_mentor_name)
capstones['mentor_key'] = capstones['Honors Mentor Clean'].apply(
	lambda x: abbreviate_name(x, first_initial_only=True).lower() if x else ''
)

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

# ---------------- Scatter ----------------
def process_faculty_folder(faculty_path, FacultyName):
	print(f"Adding honors research entries to {FacultyName}: ", end="")

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

		service_dir = faculty_path / "Service"
		filename = service_dir / "undergraduate research data.xlsx"
		if Path(filename).is_file():
			copy_with_timestamp(filename,FacultyName+os.sep+backup_dir)
		
		# ---------------- Read existing file ----------------
		excelFile = pd.read_excel(filename, sheet_name=None)
		existing_data = excelFile.get("Data", pd.DataFrame())
		notes = excelFile.get("Notes", pd.DataFrame())

		# ---------------- Merge ----------------
		result = (
			pd.concat([existing_data, toAppend], ignore_index=True)
			.drop_duplicates()
			.sort_values(
				by=["Calendar Year", "Term", "Title"],
				ascending=[True, False, True]
			)
		)

		# ---------------- Write ----------------
		with pd.ExcelWriter(filename, engine="openpyxl", mode="w") as writer:
			notes.to_excel(writer, sheet_name="Notes", index=False)
			result.to_excel(writer, sheet_name="Data", index=False)
		print(f'Appended {result.shape[0] - existing_data.shape[0]}')
	else:
		print('No entries')

# Walk the departments root to find faculty Service folders
for root, dirs, files in os.walk(departments_root):
	if 'Service' in dirs:
		faculty_path = Path(root)
		FacultyName = faculty_path.name
		if ',' in FacultyName:  # Assume faculty folders have comma
			process_faculty_folder(faculty_path, FacultyName)
			