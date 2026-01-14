#! /usr/bin/env python3

import os
import sys
import pandas as pd
from pathlib import Path
from merge_df import merge_and_dedup

if len(sys.argv) < 2:
    print("Usage: advising_eval_gather.py <faculty_root>")
    sys.exit(1)

file_source = sys.argv[1]
file_name = "advising evaluation data.xlsx"
subfolder = "Service"

collected = []
for FacultyName in os.listdir(file_source):
    if FacultyName.find(",") > -1 and Path(os.path.join(file_source, FacultyName)).is_dir():
        path = Path(file_source) / FacultyName / subfolder / file_name
        if path.is_file():
            try:
                df = pd.read_excel(path)
                df = df.copy()
                df["FacultyName"] = FacultyName
                collected.append(df)
            except Exception as e:
                print("Failed reading", path, "—", e)

if collected:
    out = merge_and_dedup(collected)
    out.to_excel(file_name, index=False)
    print("Wrote:", Path(file_name))
else:
    print("No advising evaluation files found.")
