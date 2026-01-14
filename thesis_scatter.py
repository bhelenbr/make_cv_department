#! /usr/bin/env python3

import os,sys,platform,shutil
import pandas as pd
import argparse
from pathlib import Path

from copy_with_timestamp import copy_with_timestamp
from merge_df import merge_and_dedup

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

faculty_path = Path(facultyFolder)
if not faculty_path.is_dir():
	print(f"Error: destination '{facultyFolder}' is not a directory")
	sys.exit(2)

for faculty_dir in faculty_path.iterdir():
	if not faculty_dir.is_dir():
		continue
	FacultyName = faculty_dir.name
	if FacultyName.find(",") > -1:
		print(f'Adding theses for {FacultyName} ',end='')

		lastname = FacultyName[0:FacultyName.find(",")]
        
		# Get entries for this faculty
		entries=theses[theses["Advisor"]==lastname]
		if entries.shape[0] > 0:
			toAppend = entries.iloc[:,0:7]
            
			filename = faculty_dir / destination

			# ensure parent and backup
			filename.parent.mkdir(parents=True, exist_ok=True)
			backup_path = faculty_dir / Path(backup_dir)
			backup_path.mkdir(parents=True, exist_ok=True)

			if filename.is_file():
				copy_with_timestamp(filename, str(backup_path))
				excelFile = pd.read_excel(filename,sheet_name='Data')
				existing_data = excelFile
			else:
				existing_data = pd.DataFrame()

			result = merge_and_dedup([existing_data, toAppend]).sort_values(by=['Year','Degree','Student'],ascending=[True,True,True])
			with pd.ExcelWriter(filename) as writer:
				result.to_excel(writer,sheet_name='Data',index=False)
			print(f'Appended {result.shape[0] - existing_data.shape[0]}')