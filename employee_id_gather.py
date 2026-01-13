#! /usr/bin/env python3

import os
import sys
import pandas as pd
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: employee_id_gather.py <faculty_root>")
    sys.exit(1)

file_source = sys.argv[1]
out_file = Path("make_cv") / "PersonalData" / "employee_ids.xlsx"

collected = []

for FacultyName in os.listdir(file_source):
    if FacultyName.find(",") > -1 and Path(os.path.join(file_source, FacultyName)).is_dir():
        path = Path(file_source) / FacultyName / "make_cv" / "PersonalData" / "employee_id.txt"
        if path.is_file():
            try:
                with open(path, "r") as f:
                    val = f.read().strip()
                collected.append({"FacultyName": FacultyName, "EMPLID": val})
            except Exception as e:
                print("Failed reading", path, "—", e)

if collected:
    df = pd.DataFrame(collected)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(out_file, index=False)
    print("Wrote:", out_file)
else:
    print("No employee ids found.")
