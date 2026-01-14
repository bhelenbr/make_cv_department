#! /usr/bin/env python3

import os
import sys
import pandas as pd
import platform
import shutil
import openpyxl
from pathlib import Path
from merge_df import merge_and_dedup

# Run this script from the Department Data folder
# This gathers service data from the faculty service data.xlsx file and compiles into a single csv file
# then converts that into the excel file "service data.xlsx"
# You may have to install pandas: pip3 install pandas
# You may have to install openpyxl: pip3 install openpyxl

# Source is faculty folder
file_source = sys.argv[1]
	
file = "service data.xlsx"

# collect in-memory instead of temp csv
collected = []

for FacultyName in os.listdir(file_source): # For each faculty member
	if FacultyName.find(",") > -1 and Path(os.path.join(file_source, FacultyName)).is_dir():
		print("Service: " + FacultyName,end="")
		try:
			sheet = pd.read_excel(file_source + os.sep + FacultyName + os.sep + "Service" + os.sep + file, engine='openpyxl', sheet_name="Data")
			sheet["FacultyName"] = FacultyName
			collected.append(sheet)
			print(" - read " + str(sheet.shape[0]) + " rows")
		except FileNotFoundError as e:
			print("Could not read file", FacultyName)

if collected:
	df = merge_and_dedup(collected)
	df.to_excel(file, index=False)
else:
	print("No data collected.")
