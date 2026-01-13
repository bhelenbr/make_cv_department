#! /usr/bin/env python3

import os
import sys
import pandas as pd
from pathlib import Path

file = "undergraduate research data.xlsx"
folder = "Service"

# Run this script from the Department Data folder
# This gathers undergraduate research data.xlsx from the undergraduate research data.xlsx file and compiles into a single csv file
# then converts that into the excel file "service data.xlsx"
# You may have to install pandas: pip3 install pandas
# You may have to install openpyxl: pip3 install openpyxl

# Source is faculty folder
file_source = sys.argv[1]
	
file = "undergraduate research data.xlsx"

# collect dataframes in memory instead of writing a temp CSV
collected = []

source_path = Path(file_source)
if not source_path.is_dir():
	print(f"Error: source '{file_source}' is not a directory")
	sys.exit(2)

for faculty_dir in source_path.iterdir(): # For each faculty member
	if not faculty_dir.is_dir():
		continue
	FacultyName = faculty_dir.name
	if FacultyName.find(",") > -1:
		print("UR: " +FacultyName, end = " ")
		try:
			path = faculty_dir / folder / file
			sheet = pd.read_excel(path, engine='openpyxl', sheet_name="Data")
			sheet["FacultyName"] = FacultyName
			collected.append(sheet)
			print(" - read " + str(sheet.shape[0]) + " rows")
		except FileNotFoundError as e:
			print("Could not read file", FacultyName)
		
if collected:
	df = pd.concat(collected, ignore_index=True)
	df.to_excel(file, index=False)
else:
	print("No data collected.")
