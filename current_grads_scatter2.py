#! /usr/bin/env python3

import os,sys,platform,shutil
import pandas as pd
import numpy as np
import datetime
import xlsxwriter
from datetime import date

pd.options.mode.chained_assignment = None  # default='warn'

# This reads the current student data then rewrites with updated notes
# You may have to install pandas: pip3 install pandas
# Python code to scatter current student data
# First argument is file to scatter

source = sys.argv[1]
file_destination = sys.argv[2]
emplid_file = "make_cv" +os.sep +"PersonalData" +os.sep +"employee_id.txt"

students = pd.read_excel(source,skiprows=1,dtype={'ID': str})
students = students[students["Career"]=="GRAD"]
print(students.columns)

students.drop(columns=['ID','Email','Career','Advisor','Email1'], axis=1, inplace=True)
students = students.fillna("")
destination = "Scholarship" +os.sep +"current student data.xlsx"
os.chdir(file_destination) # changes directory to Faculty folder

for FacultyName in os.listdir("."):
	if FacultyName.find(",") > -1:
		print(f'Adding gradiate advisees for {FacultyName}: ', end="")
		# Get employee id
		personal_folder = FacultyName +os.sep +emplid_file
		with open(personal_folder, "r") as f:
			employee_id = int(f.read().strip())
		entries = df.loc[df['Advisor ID'].astype(int) == employee_id]
		if entries.shape[0] > 0:
			entries["Student Name"] = entries["Last"] + ", " + entries["First Name"]
			entries["Current Program"] = entries["Acad Plan"]
			entries["Start Date"] = pd.to_datetime(str(date.today()))
			entries = entries.drop(columns=["Last","First Name","Acad Plan","Career","Advisor ID"])
			entries.sort_values(by=['Current Program','Start Date'],inplace=True)
			with pd.ExcelWriter(FacultyName +os.sep +destination,date_format='YYYY-MM-DD', datetime_format='YY-MM-DD') as writer:
				entries.to_excel(writer,sheet_name='Data',index=False)
			print(f'{entries.shape[0]} entries')
		else:
			print('No entries')
