#! /usr/bin/env python3

import os
import sys
import shutil
import pandas as pd
import argparse
from pathlib import Path
from make_cv.stringprotect import abbreviate_name
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

departments_root = args.destination
source = args.file
year = args.year

# ---------------- Load data ----------------
mcnair = pd.read_excel(source, sheet_name='Sheet1')

# Clean column names
mcnair.columns = [col.strip() for col in mcnair.columns]

# Filter by year
mcnair = mcnair[mcnair['YEAR'] == year]

# Clean and abbreviate mentor names
def clean_mentor_name(mentor):
    if pd.isna(mentor):
        return ''
    mentor = str(mentor).strip()
    # Remove initials like M., C., etc.
    mentor = re.sub(r'\b[A-Z]\.\s*', '', mentor).strip()
    # Remove titles
    mentor = re.sub(r'(Dr\.|Prof\.|Mr\.|Ms\.|Mrs\.)', '', mentor).strip()
    return mentor

mcnair['Faculty Clean'] = mcnair['Faculty'].apply(clean_mentor_name)
mcnair['mentor_key'] = mcnair['Faculty Clean'].apply(
    lambda x: abbreviate_name(x, first_initial_only=True).lower() if x else ''
)

# ---------------- Scatter ----------------
def process_faculty_folder(faculty_path, FacultyName):
    print(f"Adding mcnair research entries to {FacultyName}: ", end="")

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

        service_dir = faculty_path / "Service"
        filename = service_dir / "undergraduate research data.xlsx"
        backupfile = service_dir / "undergraduate research_backup.xlsx"

        # ---------------- Read existing file ----------------
        shutil.copyfile(filename, backupfile)
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