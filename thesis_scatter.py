#! /usr/bin/env python3

import os,sys,platform,shutil
import pandas as pd
import argparse
from pathlib import Path

from copy_with_timestamp import copy_with_timestamp

parser = argparse.ArgumentParser(description='This script scatters the thesis data to the faculty thesis files')
parser.add_argument('file', help='the name of the file to scatter')
parser.add_argument('destination', help='the destination folder')
parser.add_argument('-y', '--year',type=int,help='the calendar year of data to be scattered')
args = parser.parse_args()

facultyFolder = args.destination
source = args.file
backup_dir = "make_cv/Backups"

theses = pd.read_excel(source,sheet_name='Data')
theses = theses[theses["Year"] == args.year]

destination = "Scholarship" +os.sep +"thesis data.xlsx"

os.chdir(facultyFolder) # changes directory to Faculty folder

for FacultyName in os.listdir("."):
	if FacultyName.find(",") > -1:
		print(FacultyName)
		lastname = FacultyName[0:FacultyName.find(",")]
		
		# Get entries for this faculty
		entries=theses[theses["Advisor"]==lastname]
		if entries.shape[0] > 0:
			toAppend = entries.iloc[:,0:7]
			print(toAppend)
			
			filename = FacultyName +os.sep +destination
			if Path(filename).is_file():
				copy_with_timestamp(filename,FacultyName+os.sep+backup_dir)
			excelFile = pd.read_excel(filename,sheet_name='Data')
			
			result = pd.concat([excelFile, toAppend],ignore_index=True)
			result = result.drop_duplicates()
			result.sort_values(by=['Year','Degree','Student'],ascending=[True,True,True],inplace=True)
			
			
			with pd.ExcelWriter(filename) as writer:
				result.to_excel(writer,sheet_name='Data',index=False)