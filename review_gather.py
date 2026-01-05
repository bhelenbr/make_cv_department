#! /usr/bin/env python3

import os
import sys
import pandas as pd
import platform
import shutil
import openpyxl

file = "reviews data.xlsx"
folder = "Service"

# Run this script from the Department Data folder
# This gathers reviewing data from the reviews data.xlsx file and compiles into a single csv file
# then converts that into the excel file "reviews data.xlsx"
# You may have to install pandas: pip3 install pandas
# You may have to install openpyxl: pip3 install openpyxl

# Source is faculty folder
file_source = sys.argv[1]
	
#tempcsv = "temp.csv"
#compilation = open(tempcsv, 'w+')
#compilation.write("Journal, Start Date, Rounds, FacultyName\n")
#compilation.close()

df = pd.DataFrame()
for FacultyName in os.listdir(file_source): # For each faculty member
	if FacultyName[0].isalnum(): # gets rid of hidden files generated, allows for only faculty names left
		print("Reviewing: " +FacultyName)
		try:
			sheet = pd.read_excel(file_source +os.sep +FacultyName+os.sep+folder +os.sep +file, engine='openpyxl')
			sheet["FacultyName"] = FacultyName
			df =  pd.concat([df, sheet])
			#sheet.to_csv(open(tempcsv, 'a+'),index=False,header=False)
		except FileNotFoundError as e:
			print("Could not read file",FacultyName)
		
#df = pd.read_csv(tempcsv)
#os.remove(tempcsv)
excelfile = df.to_excel(file, index=False)

