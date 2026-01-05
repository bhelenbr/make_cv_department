#! /usr/bin/env python3

import os
import sys
import pandas as pd
import platform
import shutil
import openpyxl

file = "student awards data.xlsx"
folder = "Awards"

# Run this script from the Department Data folder
# This gathers thesis data from the thesis data.xlsx file and compiles into a single csv file
# then converts that into the excel file "thesis data.xlsx"
# You may have to install pandas: pip3 install pandas
# You may have to install openpyxl: pip3 install openpyxl

# Source is faculty folder
file_source = sys.argv[1]
	
tempcsv = "temp.csv"
compilation = open(tempcsv, 'w+')
compilation.write("Student,Title,Amount,Category,Type,Year,FacultyName\n")
compilation.close()

for FacultyName in os.listdir(file_source): # For each faculty member
	if FacultyName[0].isalnum(): # gets rid of hidden files generated, allows for only faculty names left
		print("Student Awards: " +FacultyName)
		try:
			sheet = pd.read_excel(file_source +os.sep +FacultyName+os.sep+folder +os.sep +file, engine='openpyxl',sheet_name="Data")
			sheet["FacultyName"] = FacultyName
			sheet.to_csv(open(tempcsv, 'a+'),columns=["Student","Title","Amount","Category","Type","Year","FacultyName"],index=False,header=False)
		except FileNotFoundError as e:
			print("Could not read file",FacultyName)
		
df = pd.read_csv(tempcsv)
os.remove(tempcsv)
excelfile = df.to_excel(file, index=False)

