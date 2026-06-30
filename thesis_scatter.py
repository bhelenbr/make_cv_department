#! /usr/bin/env python3

import os,sys,platform,shutil
import pandas as pd
import argparse
from pathlib import Path

from make_cv.copy_with_timestamp import copy_with_timestamp
from make_cv.stringprotect import abbreviate_name
from merge_df import merge_and_dedup

def modify_title_for_coadvising(row, faculty_abbrev):
	a1 = row.get("Advisor 1")
	a2 = row.get("Advisor 2")

	# Only modify if there are two advisors
	if pd.notna(a1) and pd.notna(a2):
		if a1 == faculty_abbrev and a2 != faculty_abbrev:
			return f"{row['Title']} (co-advised with {a2})"
		elif a2 == faculty_abbrev and a1 != faculty_abbrev:
			return f"{row['Title']} (co-advised with {a1})"

	return row["Title"]

parser = argparse.ArgumentParser(description='This script scatters the thesis data to the faculty thesis files')
parser.add_argument('file', help='the name of the file to scatter')
parser.add_argument('destination', help='the destination folder')
parser.add_argument('-y', '--year',type=int,help='the calendar year of data to be scattered')
args = parser.parse_args()

facultyFolder = args.destination
source = args.file
backup_dir = "make_cv/Backups"
destination = "Scholarship" +os.sep +"thesis data.xlsx"



# Columns we care about
output_columns = ["Student","Title","Year","Degree"]

theses = pd.read_excel(source)
theses = theses.rename(columns={"Degree Date": "Year"})

if args.year:
	theses = theses[theses["Year"].astype(int) >= args.year]

theses = theses[theses['Status'].str.match('Published by ProQuest')]
theses['Degree'] = theses['Degree'].apply(lambda x: x.replace("Master of Arts", "MA"))
theses['Degree'] = theses['Degree'].apply(lambda x: x.replace("Master of Science", "MS"))
theses['Degree'] = theses['Degree'].apply(lambda x: x.replace("Doctor of Philosophy", "PhD"))
theses["Advisor 1"] = theses["Advisor 1"].apply(lambda x: x.replace(", Dr. ", ", ") if pd.notna(x) else x)
theses["Advisor 2"] = theses["Advisor 2"].apply(lambda x: x.replace(", Dr. ", ", ") if pd.notna(x) else x)
theses["Advisor 1"] = theses["Advisor 1"].apply(lambda x: abbreviate_name(x,first_initial_only=True))
theses["Advisor 2"] = theses["Advisor 2"].apply(lambda x: abbreviate_name(x,first_initial_only=True) if pd.notna(x) else x)
theses['Student'] = theses['Student Last Name'] + ", " + theses['Student First Name']


faculty_path = Path(facultyFolder)
if not faculty_path.is_dir():
	print(f"Error: destination '{facultyFolder}' is not a directory")
	sys.exit(2)

for faculty_dir in faculty_path.iterdir():
	FacultyName = faculty_dir.name

	if not faculty_dir.is_dir() or not FacultyName.find(",") > -1:
		continue
	
	print(f'Adding theses for {FacultyName} ',end='')

	abbrev = abbreviate_name(FacultyName,first_initial_only=True)
	
	# Get entries for this faculty
	entries = theses[(theses["Advisor 1"] == abbrev) | (theses["Advisor 2"] == abbrev)].copy()
	
	if entries.empty:
		print("— none found")
		continue

	# Modify thesis titles for co-advised cases
	entries["Title"] = entries.apply(
		modify_title_for_coadvising,
		axis=1,
		faculty_abbrev=abbrev
	)

	toAppend = entries[output_columns]

	filename = faculty_dir / destination

	if filename.is_file():
		backup_path = faculty_dir / backup_dir
		copy_with_timestamp(filename, str(backup_path))
		existing_data = pd.read_excel(filename, sheet_name='Data')
	else:
		existing_data = pd.DataFrame(columns=output_columns)

	result = (
		merge_and_dedup([existing_data, toAppend], ignore_cols=['Title','Comments','Start Date'])
		.sort_values(by=["Year", "Degree", "Student"])
	)

	with pd.ExcelWriter(filename) as writer:
		result.to_excel(writer, sheet_name='Data', index=False)

	print(f"appended {result.shape[0] - existing_data.shape[0]}")