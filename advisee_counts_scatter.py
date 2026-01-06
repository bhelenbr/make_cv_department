#! /usr/bin/env python3
# import modules
import os,sys,platform,shutil
import pandas as pd
import re
import xlrd
from pathlib import Path
from datetime import date

from make_cv.stringprotect import abbreviate_name_list

source = sys.argv[1]
facultyFolder = sys.argv[2]
df = pd.read_excel(source,skiprows=1,dtype={'ID': str})
destination = "Service" +os.sep +"advisee counts.xlsx"
emplid_file = "make_cv" +os.sep +"PersonalData" +os.sep +"employee_id.txt"

today = date.today()
year = today.year
df["YEAR"] = year

os.chdir(facultyFolder) # changes directory to Faculty folder

for FacultyName in os.listdir("."):
	if FacultyName.find(",") > -1:
		print(f'Adding Advisor Counts for {FacultyName} ',end='')
		personal_folder = FacultyName +os.sep +emplid_file
		with open(personal_folder, "r") as f:
			employee_id = int(f.read().strip())
		
		# Get entries for this faculty
		entries=df.loc[df["ID"].astype(int) == employee_id]
		if entries.shape[0] > 0:
			toAppend = entries[["Advisor Name","Count Distinct Name","YEAR"]]			
			filename = FacultyName +os.sep +destination
			if Path(filename).is_file():
				excelFile = pd.read_excel(filename)
				result = pd.concat([excelFile, toAppend],ignore_index=True)
				result = result.drop_duplicates()
				result.sort_values(by=['YEAR'],ascending=[True],inplace=True)
				with pd.ExcelWriter(filename) as writer:
					result.to_excel(writer,index=False)
				print(f'Appended {result.shape[0]-excelFile.shape[0]} entries')

			else:
				with pd.ExcelWriter(filename) as writer:
					toAppend.to_excel(writer,index=False)
				print(f'Created file with {toAppend.shape[0]} entries')
		else:
			print('Not Found')
