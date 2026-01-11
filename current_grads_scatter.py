#! /usr/bin/env python3

import os,sys,platform,shutil
import pandas as pd
import numpy as np
import datetime
import xlsxwriter
from pathlib import Path

pd.options.mode.chained_assignment = None  # default='warn'

# This reads the current student data then rewrites with updated notes
# You may have to install pandas: pip3 install pandas
# Python code to scatter current student data
# First argument is file to scatter

# Destination is faculty folder
if platform.system() == 'Windows':
	file_destination = r"S:\departments\Mechanical & Aerospace Engineering\Faculty"
else:
	file_destination = r"/Volumes/Mechanical & Aerospace Engineering/Faculty"

source = sys.argv[1]
students = pd.read_excel(source,sheet_name='Current Students')
students.drop(students.columns[7:], axis=1, inplace=True)
students = students.fillna("")
destination = "Scholarship" +os.sep +"current student data.xlsx"
os.chdir(file_destination) # changes directory to Faculty folder

for FacultyName in os.listdir("."):
	if FacultyName.find(",") > -1:
		lastname = FacultyName.lower()[0:FacultyName.find(",")]
		entries=students[students["Advisor"].apply(lambda x: x.lower().find(lastname) != -1)]
		if entries.shape[0] > 0:
			print(FacultyName)
			entries["Student Name"] = entries["Student Name"].apply(lambda x: x[0:x.find("(")])
			entries["Start Date"] = np.where(entries['PhD Start Date'].apply(lambda x: False if pd.isnull(x) else True), entries['PhD Start Date'], entries['MS Start Date'])
			entries["Start Date"] = pd.to_datetime(entries["Start Date"])
			entries.drop(columns=['Advisor', 'Initial Program','MS Start Date', 'MS Finish Date', 'PhD Start Date'],inplace=True)
			entries.sort_values(by=['Current Program','Start Date'],inplace=True)
			print(entries)
			with pd.ExcelWriter(FacultyName +os.sep +destination,date_format='YYYY-MM-DD', datetime_format='YY-MM-DD') as writer:
				entries.to_excel(writer,sheet_name='Data',index=False)
