#! /usr/bin/env python3

# This code will be used to transfer individual professor evaluation data to their respective data files
# from the master evaluation spreadsheet

# import modules
import pandas as pd
import os
import platform
from make_cv.stringprotect import abbreviate_name

# Destination is faculty folder
if platform.system() == 'Windows':
	file_destination = r"S:\departments\Mechanical & Aerospace Engineering\Faculty"
	os.chdir(r"S:\departments\Mechanical & Aerospace Engineering\Confidential Information\Department Data\Teaching")
else:
	file_destination = r"/Volumes/Mechanical & Aerospace Engineering/Faculty"
	os.chdir(r"/Volumes/Mechanical & Aerospace Engineering/Confidential Information/Department Data/Teaching")
	
df = pd.read_excel('Teaching Eval Data.xlsx',"Data")
df.fillna(value={"INSTR_NA":""},inplace=True)
df['INSTR_NA'] = df['INSTR_NA'].apply(lambda x : abbreviate_name(x,first_initial_only=True))
sorted = df.sort_values(by="INSTR_NA",ignore_index=True)
nrows = sorted.shape[0]
os.chdir(file_destination) # where files need to go

count = 1
while count < nrows:
	advisor = sorted.loc[count,'INSTR_NA']
	entries=sorted[sorted["INSTR_NA"]==advisor]
	entries.reset_index(inplace=True)
	for FacultyName in os.listdir("."):
		if FacultyName[0].isalnum():
			abbrv = abbreviate_name(FacultyName,first_initial_only=True)
			if advisor == abbrv:
				print(abbrv)
				#print(entries.head())
				with pd.ExcelWriter(FacultyName + "/Teaching/" + "/teaching evaluation data.xlsx") as writer:
					entries.to_excel(writer,sheet_name='Data',index=False)
	count += entries.shape[0]
