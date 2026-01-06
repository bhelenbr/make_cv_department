#! /usr/bin/env python3
# import modules
import os,sys,platform,shutil
import pandas as pd
import re
import xlrd
from pathlib import Path
from datetime import date

from make_cv.stringprotect import abbreviate_name

source = sys.argv[1]
facultyFolder = sys.argv[2]
destination = "Proposals & Grants" +os.sep +"expenditures.xlsx"
emplid_file = "make_cv" +os.sep +"PersonalData" +os.sep +"employee_id.txt"

df = pd.read_excel(source,skiprows=1,dtype={'EMPLID': str})
df["Name"] = (
	df["Name"]
	.astype(str)
	.apply(lambda x: abbreviate_name(x,first_initial_only=True).lower())
)
df.drop(['F(Fiscal Year) or C(Calendar)','Start Term','End Term','Year1'], axis=1,inplace=True)

os.chdir(facultyFolder) # changes directory to Faculty folder

for FacultyName in os.listdir("."):
	if FacultyName.find(",") > -1:
		print(f'Updating expenditures for {FacultyName} ',end='')
		personal_folder = FacultyName +os.sep +emplid_file
		with open(personal_folder, "r") as f:
			employee_id = int(f.read().strip())
			
		# Get entries for this faculty
		entries=df.loc[df["EMPLID"].astype(int) == employee_id]
		entries = entries.drop(columns = ["EMPLID"])
		if entries.shape[0] > 0:
			filename = FacultyName +os.sep +destination
			if Path(filename).is_file():
				excelFile = pd.read_excel(filename)
				result = pd.concat([excelFile, entries],ignore_index=True)
				result = result.drop_duplicates()
				result.sort_values(by=['Year'],ascending=[True],inplace=True)
				with pd.ExcelWriter(filename) as writer:
					result.to_excel(writer,index=False)
				print(f'Appended {result.shape[0] -excelFile.shape[0]}')
			else:
				with pd.ExcelWriter(filename) as writer:
					entries.to_excel(writer,index=False)
				print(f'Added {entries.shape[0]}')
		else:
			print('No entries')
