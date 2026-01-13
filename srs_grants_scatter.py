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
from merge_df import merge_keep_old_columns


source = sys.argv[1]
faculty_folder = sys.argv[2]
emplid_file = Path("make_cv") / "PersonalData" / "employee_id.txt"
backup_dir = "make_cv/Backups"
subfolder = "Proposals & Grants"
file_name = "grants.xlsx"

# Read the desired source file, which is the updated Proposal and Grants file with new entries
df = pd.read_excel(source,skiprows=1,dtype={'Faculty ID': str})

# Try to make the grant data look like the proposal data
new_column_names = {   
"Contributor Type": "Role",
"Funding Agency / Sponsor": "Sponsor",
"Award Start Date": "Begin Date",
"Award End Date": "End Date",
"Grouped Award ID": "Proposal_ID",
"Award Total Funding":"Allocated Amt",
"Percent Effort":"PCT",
"Faculty ID":"ID"
}
df.rename(columns=new_column_names, inplace=True)
df["Faculty"] = (
	(df["First Name"].astype(str) +" " +df["Last Name"].astype(str))
	.apply(lambda x: abbreviate_name(x,first_initial_only=True).lower())
)
df["Total Cost"] = df["Allocated Amt"]/df["PCT"].astype(float)*100.
df.drop(["First Name","Last Name","Award Status","Total # of Funding Periods","Award ID / Contract ID"], axis=1,inplace=True)

faculty_path = Path(faculty_folder)
if not faculty_path.is_dir():
	print(f"Error: destination '{faculty_folder}' is not a directory")
	sys.exit(2)

for faculty_dir in faculty_path.iterdir():
	if not faculty_dir.is_dir():
		continue
	FacultyName = faculty_dir.name
	if FacultyName.find(",") > -1:
		# Get employee id
		personal_folder = faculty_dir / emplid_file
		if not personal_folder.is_file():
			print(f"Skipping {FacultyName} (missing employee_id)")
			continue
		with open(personal_folder, "r") as f:
			try:
				employee_id = int(f.read().strip())
			except Exception:
				print(f"Skipping {FacultyName} (invalid employee_id)")
				continue
		entries=df.loc[df["ID"].astype(int) == employee_id]
		entries = entries.drop(columns = ["ID"])
		idx = entries.groupby("Proposal_ID")["Budget Period"].idxmax()
		entries = entries.loc[idx]
		entries = entries.drop(columns = ["Budget Period"])
		entries = entries.set_index("Proposal_ID",drop=True)
        
		print(f"Adding grants to {FacultyName}: ", end ="")
		destination = faculty_dir / subfolder / file_name

		# ensure parent and backup dirs
		destination.parent.mkdir(parents=True, exist_ok=True)
		backup_path = faculty_dir / Path(backup_dir)
		backup_path.mkdir(parents=True, exist_ok=True)

		if destination.is_file():
			copy_with_timestamp(destination, str(backup_path))
			excelFile = pd.read_excel(destination, sheet_name=None,dtype={'Proposal_ID': str})
			df_old = excelFile.get("Data", pd.DataFrame())
			notes = excelFile.get("Notes", pd.DataFrame())
            
			# generate duplicate counters per value and modify "Proposal_ID" so that it is unique
			dupe_count = df_old.groupby("Proposal_ID").cumcount()
			# map 1 → 'b', 2 → 'c', ...
			suffix = dupe_count.map(lambda x: "" if x == 0 else chr(ord('a') + x))
			df_old["Proposal_ID"] = df_old["Proposal_ID"] + suffix
			# set as index
			df_old = df_old.set_index("Proposal_ID",drop=True)
			merged = merge_keep_old_columns(entries,df_old,cols_from_old=["Sponsor", "Title"])
			with pd.ExcelWriter(destination, engine="openpyxl", mode="w") as writer:
				notes.to_excel(writer, sheet_name="Notes", index=False)
				merged.to_excel(writer, sheet_name="Data", index=True)
			print(f'Appended {merged.shape[0]-df_old.shape[0]} grants')
		else:
			with pd.ExcelWriter(destination, engine="openpyxl", mode="w") as writer:
				entries.to_excel(writer, sheet_name="Data",index=True)
				notes = pd.DataFrame()
				notes.to_excel(writer, sheet_name="Notes", index=False)
			print(f'New {entries.shape[0]} grants')

			