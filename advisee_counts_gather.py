#! /usr/bin/env python3

import os
import sys
import pandas as pd
from pathlib import Path
from merge_df import merge_and_dedup

file = "advisee counts.xlsx"
folder = "Service"

# Source is faculty folder
if len(sys.argv) < 2:
    print("Usage: advisee_counts_gather.py <faculty_root>")
    sys.exit(1)

file_source = sys.argv[1]

# collect in-memory instead of temp csv
collected = []

for FacultyName in os.listdir(file_source):
    if FacultyName.find(",") > -1 and Path(os.path.join(file_source, FacultyName)).is_dir():
        print("Advisee Counts: " + FacultyName,end="")
        try:
            path = os.path.join(file_source, FacultyName, folder, file)
            # try reading the standard sheet name used by advisee_counts
            sheet = pd.read_excel(path, engine='openpyxl', sheet_name="Sheet1")
            sheet['Advisor Name'] = FacultyName
            collected.append(sheet)
            print(" - read " + str(sheet.shape[0]) + " rows")
        except FileNotFoundError:
            print("Could not read file", FacultyName)
        except Exception as e:
            print("Failed reading", path, "—", e)

if collected:
    df = merge_and_dedup(collected)
    df.to_excel(file, index=False)
    print("Wrote:", file)
else:
    print("No data collected.")
