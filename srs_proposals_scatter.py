#! /usr/bin/env python3

# Python code to scatter Proposals and Grants data to faculty Proposals and Grants folder
# First argument is file to scatter, second argument is Faculty
# scatter <file to scatter> <Faculty folder>

# import modules
import pandas as pd
import os
import sys
import platform
from os.path import exists
from pathlib import Path

from make_cv.stringprotect import abbreviate_name
from copy_with_timestamp import copy_with_timestamp

new_column_names = {   
'P_STATUS': 'Role',
'Name': 'Faculty', 
'Name.1': 'Sponsor',
'Status': 'Funded?',
'Long Descr': 'Title'
}

emplid_file = "make_cv" +os.sep +"PersonalData" +os.sep +"employee_id.txt"
backup_dir = "make_cv/Backups"

def merge_proposals(df_new, destination):
	if exists(destination):
		excelFile = pd.read_excel(destination, sheet_name=None,dtype={'Proposal_ID': str})
		df_old = excelFile.get("Data", pd.DataFrame())
		notes = excelFile.get("Notes", pd.DataFrame())
		
		# generate duplicate counters per value
		dupe_count = df_old.groupby("Proposal_ID").cumcount()

		# map 1 → 'b', 2 → 'c', ...
		suffix = dupe_count.map(lambda x: "" if x == 0 else chr(ord('a') + x))

		df_old["Proposal_ID"] = df_old["Proposal_ID"] + suffix
		
		# set as index
		df_old = df_old.set_index("Proposal_ID")
		
		# Proposal_ID		Sponsor	Allocated Amt	Total Cost	Funded?	Title	Begin Date	End Date	Submit Date	Principal Investigators
		#values = {"Role": "PI", "Funded?": "No"}
		df_old.fillna("",inplace=True)

		# keep only truly new proposal IDs
		new_rows = df_new.loc[~df_new.index.isin(df_old.index)]
		print(f" adding {len(new_rows)} rows")
		# insert new rows by index
		df_old = df_old.reindex(df_old.index.union(new_rows.index))
		df_old.update(new_rows)

		with pd.ExcelWriter(destination, engine="openpyxl", mode="w") as writer:
			notes.to_excel(writer, sheet_name="Notes", index=False)
			df_old.to_excel(writer, sheet_name="Data", index=True)

	else:
		with pd.ExcelWriter(destination, engine="openpyxl", mode="w") as writer:
			df_new.to_excel(writer, sheet_name="Data",index=True)
			notes = pd.DataFrame()
			notes.to_excel(writer, sheet_name="Notes", index=False)

# Read the desired source file, which is the updated Proposal and Grants file with new entries
source = sys.argv[1]
df = pd.read_excel(source,index_col='Proposal',skiprows=1)
df.rename(columns=new_column_names, inplace=True)
df.drop(['Project','PCT','RO Number'], axis=1,inplace=True)
df["Faculty"] = (
	df["Faculty"]
	.astype(str)
	.apply(lambda x: abbreviate_name(x,first_initial_only=True).lower())
)
df.index.name = "Proposal_ID"

faculty_folder = sys.argv[2]
subfolder = "Proposals & Grants"
file_name = "proposals & grants.xlsx"

for FacultyName in os.listdir(faculty_folder):
	if FacultyName.find(",") > -1:
		# Get employee id
		personal_folder = faculty_folder+os.sep +FacultyName +os.sep +emplid_file
		with open(personal_folder, "r") as f:
			employee_id = int(f.read().strip())
		entries=df.loc[df["ID"].astype(int) == employee_id]
		entries = entries.drop(columns = ["ID"])
		print(f"Adding proposals & grants to {FacultyName}: {str(len(entries))}", end ="")
		destination = faculty_folder+os.sep +FacultyName +os.sep +subfolder +os.sep +file_name
		if Path(destination).is_file():
			copy_with_timestamp(destination,FacultyName+os.sep+backup_dir)
		merge_proposals(entries,destination)
