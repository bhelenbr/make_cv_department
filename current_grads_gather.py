#! /usr/bin/env python3

import os
import sys
import pandas as pd
import platform
import shutil
import openpyxl
from pathlib import Path

file = "current student data.xlsx"
folder = "Scholarship"

# Run this script from the Department Data folder
# This gathers thesis data from the thesis data.xlsx file and compiles into a single csv file
# then converts that into the excel file "thesis data.xlsx"
# You may have to install pandas: pip3 install pandas
# You may have to install openpyxl: pip3 install openpyxl

# Source is faculty folder
file_source = sys.argv[1]
	
# collect in-memory instead of temp csv
collected = []

for FacultyName in os.listdir(file_source): # For each faculty member
	if FacultyName.find(",") > -1 and Path(os.path.join(file_source, FacultyName)).is_dir():
		print("Current Grads: " + FacultyName,e)
		try:
			sheet = pd.read_excel(file_source + os.sep + FacultyName + os.sep + folder + os.sep + file, engine='openpyxl', sheet_name="Data")
			sheet["FacultyName"] = FacultyName
			collected.append(sheet[["Student Name", "Current Program", "Start Date", "FacultyName"]])
			print(" - read " + str(sheet.shape[0]) + " rows")
		except FileNotFoundError as e:
			print("Could not read file", FacultyName)

if collected:
	df = pd.concat(collected, ignore_index=True)
	df.to_excel(file, index=False)
else:
	print("No data collected.")

