#! /usr/bin/env python3

# This code will be used to transfer individual professor evaluation data to their respective data files
# from the master evaluation spreadsheet

# import modules
import pandas as pd
import os
import platform
import sys
from pathlib import Path
import openpyxl

from make_cv.stringprotect import abbreviate_name
from copy_with_timestamp import copy_with_timestamp

import sys
import os
from pathlib import Path
import pandas as pd

faculty_dir = sys.argv[2]
source_file = sys.argv[1]
backup_dir = "make_cv/Backups"

# --- Load data ---
df = pd.read_excel(source_file)

df.fillna(value={"Staff": "", "Deposit": ""}, inplace=True)

df["Deposit"] = (df["Deposit"] == "Deposit").astype(int)

df["Staff"] = df["Staff"].apply(
	lambda x: abbreviate_name(x.split("-")[0].strip()) if "-" in x else abbreviate_name(x,first_initial_only=True)
)

df["Year"] = df["Date of Visit"].astype(str).str[:4].astype(int)

# --- Aggregate ---
table = (
	df.groupby(["Staff", "Year"])
	  .agg(
		  Visits=("Person Last", "count"),
		  Deposits=("Deposit", "sum")
	  )
	  .reset_index()
)

# --- Write per faculty ---
os.chdir(faculty_dir)

for advisor, entries in table.groupby("Staff"):
	
	for FacultyName in os.listdir("."):
		if not FacultyName[0].isalnum():
			continue

		
		if advisor.lower().find(abbreviate_name(FacultyName,first_initial_only=True)) == -1:
			continue
		
		filename = (
			FacultyName
			+ os.sep
			+ "Service"
			+ os.sep
			+ "prospective visit data.xlsx"
		)

		Path(filename).parent.mkdir(parents=True, exist_ok=True)

		if Path(filename).is_file():
			copy_with_timestamp(filename,FacultyName+os.sep+backup_dir)
			existing = pd.read_excel(filename)
			result = (
				pd.concat([existing, entries], ignore_index=True)
				  .drop_duplicates()
				  .sort_values(by=["Year"])
			)
		else:
			result = entries.sort_values(by=["Year"])
		
		with pd.ExcelWriter(filename, engine="openpyxl", mode="w") as writer:
			result.to_excel(writer, index=False)
	
