#! /usr/bin/env python3

import os
import sys
import pandas as pd
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: grants_gather.py <faculty_root>")
    sys.exit(1)

file_source = sys.argv[1]
file_name = "grants.xlsx"
subfolder = "Proposals & Grants"

collected = []
for FacultyName in os.listdir(file_source):
    if FacultyName.find(",") > -1 and Path(os.path.join(file_source, FacultyName)).is_dir():
        path = Path(file_source) / FacultyName / subfolder / file_name
        if path.is_file():
            try:
                # grants files often use an index; read as DataFrame
                df = pd.read_excel(path, sheet_name=None)
                # try to use 'Data' sheet if present, else default
                if 'Data' in df:
                    df = df['Data']
                else:
                    # if sheet_name None returns dict, pick first sheet
                    if isinstance(df, dict):
                        df = list(df.values())[0]
                df = df.copy()
                df["FacultyName"] = FacultyName
                collected.append(df)
            except Exception as e:
                print("Failed reading", path, "—", e)

if collected:
    out = pd.concat(collected, ignore_index=True)
    out.to_excel(file_name, index=False)
    print("Wrote:", file_name)
else:
    print("No grants files found.")
