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

print(abbreviate_name('Costel,Darie C',first_initial_only=True).lower())
df = pd.read_excel(source,skiprows=1)
df["Name"] = (
	df["Name"]
	.astype(str)
	.apply(lambda x: abbreviate_name(x,first_initial_only=True).lower())
)
df.drop(['F(Fiscal Year) or C(Calendar)','Start Term','End Term','Year1','EMPLID'], axis=1,inplace=True)

os.chdir(facultyFolder) # changes directory to Faculty folder

for FacultyName in os.listdir("."):
	if FacultyName.find(",") > -1:
		name = abbreviate_name(FacultyName,first_initial_only=True).lower();
		print(name)
		
		# Get entries for this faculty
		entries=df[df["Name"]==name]
		if entries.shape[0] > 0:
			print(entries)
			filename = FacultyName +os.sep +destination
			if Path(filename).is_file():
				excelFile = pd.read_excel(filename)
				result = pd.concat([excelFile, entries],ignore_index=True)
				result = result.drop_duplicates()
				result.sort_values(by=['Year'],ascending=[True],inplace=True)
				with pd.ExcelWriter(filename) as writer:
					result.to_excel(writer,index=False)
			else:
				with pd.ExcelWriter(filename) as writer:
					entries.to_excel(writer,index=False)
