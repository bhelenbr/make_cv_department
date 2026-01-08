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
from make_cv.stringprotect import abbreviate_name

# TITLES IN SOURCE DATA
# "Faculty ID","First Name","Last Name","Contributor Type","Percent Effort","Grouped Award ID","Budget Period","Principal Investigators","Award Status","Title","Award Start Date","Award End Date","Funding Agency / Sponsor","Total # of Funding Periods","Award ID / Contract ID","Award Total Funding","Award Total Direct Funding"

# TITLES IN DESTINATION
# "Proposal_ID","Faculty","Sponsor","Allocated Amt","Total Cost","Funded?","Title","Begin Date","End Date","Submit Date","Principal Investigators"

# TITLES IN PROPOSAL SOURCE
#"Proposal","Project","ID","Name","PCT","P_STATUS","Principal Investigators","Name","Allocated Amt","Total Cost","Status","Long Descr","Begin Date","End Date","RO Number","Submit Date"

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

emplid_file = "make_cv" +os.sep +"PersonalData" +os.sep +"employee_id.txt"

# This to allow people to modify the Sponsor or Title for better formatting etc...
def merge_keep_old_columns(df_new, df_old, cols_from_old):
    # Join old columns onto new dataframe by index
    df_merged = df_new.join(df_old[list(cols_from_old)], how="left", rsuffix="_old")

    # Overwrite new columns with old values where available
    for col in cols_from_old:
        if col in df_merged:
            df_merged[col] = df_merged[f"{col}_old"].combine_first(df_merged[col])
            df_merged.drop(columns=f"{col}_old", inplace=True)

    return df_merged
    
def merge_proposals(df_new, destination):
	if exists(destination):
		excelFile = pd.read_excel(destination, sheet_name=None,dtype={'Proposal_ID': str})
		df_old = excelFile.get("Data", pd.DataFrame())
		notes = excelFile.get("Notes", pd.DataFrame())
		
		# generate duplicate counters per value and modify "Proposal_ID" so that it is unique
		# This is just in case someone adds something without a unique Proposal ID
		dupe_count = df_old.groupby("Proposal_ID").cumcount()
		# map 1 → 'b', 2 → 'c', ...
		suffix = dupe_count.map(lambda x: "" if x == 0 else chr(ord('a') + x))
		df_old["Proposal_ID"] = df_old["Proposal_ID"] + suffix
		# set as index
		df_old = df_old.set_index("Proposal_ID",drop=True)
		
		merged = merge_keep_old_columns(df_new,df_old,cols_from_old=["Sponsor", "Title"])
		with pd.ExcelWriter(destination, engine="openpyxl", mode="w") as writer:
			notes.to_excel(writer, sheet_name="Notes", index=False)
			merged.to_excel(writer, sheet_name="Data", index=True)
		print(f'Appended {merged.shape[0]-df_old.shape[0]} grants')

	else:
		with pd.ExcelWriter(destination, engine="openpyxl", mode="w") as writer:
			df_new.to_excel(writer, sheet_name="Data",index=True)
			notes = pd.DataFrame()
			notes.to_excel(writer, sheet_name="Notes", index=False)
		print(f'New {df_new.shape[0]} grants')

# Read the desired source file, which is the updated Proposal and Grants file with new entries
source = sys.argv[1]
df = pd.read_excel(source,skiprows=1,dtype={'Faculty ID': str})

# Try to make the grant data look like the proposal data
df.rename(columns=new_column_names, inplace=True)

idx = df.groupby("Proposal_ID")["Budget Period"].idxmax()
df = df.loc[idx]
df["Faculty"] = (
	(df["First Name"].astype(str) +" " +df["Last Name"].astype(str))
	.apply(lambda x: abbreviate_name(x,first_initial_only=True).lower())
)
df["Total Cost"] = df["Allocated Amt"]/df["PCT"].astype(float)*100.
df.drop(["First Name","Last Name","Budget Period","Award Status","Total # of Funding Periods","Award ID / Contract ID"], axis=1,inplace=True)

faculty_folder = sys.argv[2]
subfolder = "Proposals & Grants"
file_name = "grants.xlsx"

for FacultyName in os.listdir(faculty_folder):
	if FacultyName.find(",") > -1:
		# Get employee id
		personal_folder = faculty_folder+os.sep +FacultyName +os.sep +emplid_file
		with open(personal_folder, "r") as f:
			employee_id = int(f.read().strip())
		entries=df.loc[df["ID"].astype(int) == employee_id]
		entries = entries.drop(columns = ["ID"])
		entries = entries.set_index("Proposal_ID",drop=True)
		
		print(f"Adding proposals & grants to {FacultyName}: ", end ="")
		merge_proposals(entries,faculty_folder+os.sep +FacultyName +os.sep +subfolder +os.sep +file_name)
