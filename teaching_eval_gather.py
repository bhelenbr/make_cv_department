#! /usr/bin/env python3

import os
import sys
import pandas as pd
from pathlib import Path
from merge_df import merge_and_dedup

if len(sys.argv) < 2:
    print("Usage: teaching_eval_gather.py <faculty_root>")
    sys.exit(1)

file_source = sys.argv[1]
file_name = "teaching evaluation data.xlsx"
subfolder = "Teaching"

collected = []
for FacultyName in os.listdir(file_source):
    if FacultyName.find(",") > -1 and Path(os.path.join(file_source, FacultyName)).is_dir():
        path = Path(file_source) / FacultyName / subfolder / file_name
        if path.is_file():
            try:
                df = pd.read_excel(path, sheet_name='Data') if 'Data' in pd.ExcelFile(path).sheet_names else pd.read_excel(path)
                df = df.copy()
                df["FacultyName"] = FacultyName
                collected.append(df)
            except Exception as e:
                print("Failed reading", path, "—", e)

if collected:
    out = merge_and_dedup(collected)
    out.to_excel(file_name, index=False)
    print("Wrote:", file_name)
else:
    print("No teaching evaluation files found.")
