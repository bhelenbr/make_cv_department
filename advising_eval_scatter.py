#! /usr/bin/env python3

# This code will be used to transfer individual professor evaluation data to their respective data files
# from the master evaluation spreadsheet

# import modules
import pandas as pd
import os
import platform
import sys
from pathlib import Path

faculty_dir = sys.argv[2]
source_file = sys.argv[1]
emplid_file = "make_cv" +os.sep +"PersonalData" +os.sep +"employee_id.txt"


df = pd.read_excel(source_file,skiprows=1,dtype={'ID': str})

os.chdir(faculty_dir) # where files need to go

count = 1
for FacultyName in os.listdir("."):
	if FacultyName.find(",") > -1:
		print(f'Adding advising evals for {FacultyName}: ', end="")
		# Get employee id
		personal_folder = FacultyName +os.sep +emplid_file
		with open(personal_folder, "r") as f:
			employee_id = int(f.read().strip())
			
		entries = df.loc[df['ID'].astype(int) == employee_id]
		if entries.shape[0] > 0:
			filename = FacultyName +os.sep +"Service" +os.sep +"advising evaluation data.xlsx"
			if Path(filename).is_file():
				excelFile = pd.read_excel(filename,dtype={'ID': str})
				startsize = excelFile.shape[0]
				result = pd.concat([excelFile, entries],ignore_index=True)
				result = result.drop_duplicates()
				result.sort_values(by=['Term','Number'],ascending=[True,True],inplace=True)					
				with pd.ExcelWriter(filename) as writer:
					result.to_excel(writer,index=False)
				print(f'Appended {result.shape[0] -startsize}')
			else:
				with pd.ExcelWriter(filename) as writer:
					entries.to_excel(writer,index=False)
				print(f'Added {entries.shape[0]}')
		else:
			print('No new entries')