#! /usr/bin/env python3

import os
import sys
import pandas as pd
import platform
import shutil
import openpyxl
from pathlib import Path

file = "reviews data.xlsx"
folder = "Service"

# Run this script from the Department Data folder
# This gathers reviewing data from the reviews data.xlsx file and compiles into a single csv file
# then converts that into the excel file "reviews data.xlsx"
# You may have to install pandas: pip3 install pandas
# You may have to install openpyxl: pip3 install openpyxl

# Source is faculty folder
file_source = sys.argv[1]

df = pd.DataFrame()
for FacultyName in os.listdir(file_source): # For each faculty member
	if FacultyName.find(",") > -1 and Path(os.path.join(file_source, FacultyName)).is_dir():
		print("Reviewing: " + FacultyName)
		try:
			sheet = pd.read_excel(file_source +os.sep +FacultyName+os.sep+folder +os.sep +file, engine='openpyxl')
			sheet["FacultyName"] = FacultyName
			df =  pd.concat([df, sheet])
			print(" - read " + str(sheet.shape[0]) + " rows")
		except FileNotFoundError as e:
			print("Could not read file",FacultyName)
		
if not df.empty:
	excelfile = df.to_excel(file, index=False)
else:
	print("No data collected.")

