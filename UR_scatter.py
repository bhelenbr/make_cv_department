#! /usr/bin/env python3

# Python code to scatter Undergraduate research data to faculty folders
# argument is file to scatter

# import modules
import os,sys,platform,shutil
import pandas as pd
import re
import xlrd

from make_cv.stringprotect import abbreviate_name
from make_cv.stringprotect import abbreviate_name_list

source = sys.argv[1]
facultyFolder = sys.argv[2]
emplid_file = "make_cv" +os.sep +"PersonalData" +os.sep +"employee_id.txt"
destination = "Service" +os.sep +"undergraduate research data.xlsx"

df = pd.read_excel(source,skiprows=1,dtype={'Advisor ID': str})
classnum = df["Class"].apply(lambda x: int(x[-3:]))
df = df[classnum < 499]
df = df[df['Title'] != 'Aircraft Design I']
df = df[df['Title'] != 'Professional Experience']
df['Calendar Year'] = df['Term'].apply(lambda x: int(x[-4:]))
df['Term'] = df['Term'].apply(lambda x: x[:-5])
df['Program Type'] = df['Program Type'].apply(lambda x: re.sub("Independent Study","Ind. Proj.",re.sub("Research","Und. Res.",x)))
df = df.rename(columns={"Student Name": "Students"})
df['Students'] = df['Students'].apply(lambda x: abbreviate_name_list(x))

os.chdir(facultyFolder) # changes directory to Faculty folder

for FacultyName in os.listdir("."):	
	if FacultyName.find(",") > -1:
		print(f'Adding undergraduate research classes for {FacultyName} ',end='')
		personal_folder = FacultyName +os.sep +emplid_file
		with open(personal_folder, "r") as f:
			employee_id = int(f.read().strip())
		
		# Get entries for this faculty
		entries=df.loc[df["Advisor ID"].astype(int) == employee_id]
		if entries.shape[0] > 0:
			toAppend = entries[['Students','Title','Program Type','Term','Calendar Year']]			
			filename = FacultyName +os.sep +destination
			excelFile = pd.read_excel(filename,sheet_name='Data')
			
			result = pd.concat([excelFile, toAppend],ignore_index=True)
			result = result.drop_duplicates()
			result.sort_values(by=['Calendar Year','Term','Program Type','Students'],ascending=[True,False,True,True],inplace=True)
			
			with pd.ExcelWriter(filename) as writer:
				result.to_excel(writer,sheet_name='Data',index=False)
			print(f'Appended {result.shape[0] -excelFile.shape[0]}')
		else:
			print(f'No entries')
