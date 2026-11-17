#!/usr/bin/env python3
"""
Sync a directory of make_cv faculty folders with a faculty spreadsheet.

For every row in the spreadsheet, a folder named
    "Lastname, Firstname - EmployeeID"
is created with `make_cv -b` if it does not already exist, and the employee
ID is written to make_cv/PersonalData/personal_data.txt in the new folder.

Folders in the directory that do not match anyone in the spreadsheet are
moved into an archive subfolder (default: "Archived").

If a folder already exists for an employee ID but under a different name
(e.g. a name change in the spreadsheet), it is renamed instead of being
archived and recreated, so no CV data is lost.

Usage:
    python sync_faculty_folders.py Faculty-Info.xlsx [target_dir]
        [--archive Archived] [--sheet Data] [--dry-run]
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

ID_PATTERN = re.compile(r" - (\S+)$")   # employee ID at the end of a folder name
PERSONAL_DATA = Path("make_cv") / "PersonalData" / "personal_data.txt"


def write_employee_id(folder, emp_id):
    """Set "employeeid = <id>" in the folder's personal_data.txt.

    Replaces an existing employeeid line, or appends one, leaving the other
    IDs (googleid, scopusid, orcid, ...) untouched.
    """
    path = folder / PERSONAL_DATA
    path.parent.mkdir(parents=True, exist_ok=True)
    text = path.read_text() if path.is_file() else "# Personal data (IDs) for make_cv\n"
    line = f"employeeid = {emp_id}"
    pattern = re.compile(r"(?im)^[ \t]*employeeid[ \t]*=.*$")
    if pattern.search(text):
        text = pattern.sub(line, text, count=1)
    else:
        if text and not text.endswith("\n"):
            text += "\n"
        text += line + "\n"
    path.write_text(text)


def read_faculty(xlsx, sheet):
    """Return {employee_id: folder_name} from the spreadsheet."""
    df = pd.read_excel(xlsx, dtype={"ID": str},skiprows=1)
    df.columns = [str(c).strip() for c in df.columns]
    missing = [c for c in ("ID", "First Name", "Last") if c not in df.columns]
    if missing:
        sys.exit(f"Missing expected column(s) in spreadsheet: {', '.join(missing)}")

    df = df[df["Directory Group"] == 'FAC']
    # Drop adjunct and emeritus faculty
    df = df[~df['Title'].astype(str).str.contains('Adjunct|Emeritus', case=False, na=False)]

    df = df.dropna(subset=["ID", "First Name", "Last"])
    faculty = {}
    for _, row in df.iterrows():
        emp_id = str(row["ID"]).strip()
        first = str(row["First Name"]).strip()
        last = str(row["Last"]).strip()
        if not emp_id or not first or not last:
            continue
        name = f"{last}, {first} - {emp_id}"
        # Strip characters that are illegal in file names on Windows/macOS
        name = re.sub(r'[\\/:*?"<>|]', "", name)
        faculty[emp_id] = name
    return faculty


def unique_path(path):
    """Return path, or path with ' (2)', ' (3)', ... appended if it exists."""
    if not path.exists():
        return path
    n = 2
    while True:
        candidate = path.with_name(f"{path.name} ({n})")
        if not candidate.exists():
            return candidate
        n += 1


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("xlsx", help="faculty spreadsheet (.xlsx)")
    p.add_argument("target", nargs="?", default=".",
                   help="directory holding the faculty folders (default: current)")
    p.add_argument("--archive", default="Archived",
                   help="name of archive subfolder (default: Archived)")
    p.add_argument("--sheet", default="Data",
                   help="worksheet name (default: Data)")
    p.add_argument("--dry-run", action="store_true",
                   help="show what would happen without changing anything")
    args = p.parse_args()

    target = Path(args.target).resolve()
    if not target.is_dir():
        sys.exit(f"Target directory does not exist: {target}")
    archive = target / args.archive

    faculty = read_faculty(args.xlsx, args.sheet)
    id_of = {name: emp_id for emp_id, name in faculty.items()}
    wanted = set(faculty.values())
    print(f"{len(faculty)} faculty in spreadsheet")

    # Existing folders (ignore the archive folder and hidden folders)
    existing = [d for d in target.iterdir()
                if d.is_dir() and d.name != args.archive and not d.name.startswith(".")]

    created = renamed = archived = 0
    present = {d.name for d in existing}

    # 1. Rename folders whose employee ID matches but whose name changed
    for d in existing:
        if d.name in wanted:
            continue
        m = ID_PATTERN.search(d.name)
        if m and m.group(1) in faculty and faculty[m.group(1)] not in present:
            new = target / faculty[m.group(1)]
            print(f"RENAME   {d.name}  ->  {new.name}")
            if not args.dry_run:
                d.rename(new)
            present.discard(d.name)
            present.add(new.name)
            renamed += 1

    # 2. Archive folders that don't belong to anyone in the spreadsheet
    for name in sorted(present - wanted):
        dest = unique_path(archive / name)
        print(f"ARCHIVE  {name}  ->  {args.archive}/{dest.name}")
        # if not args.dry_run:
        #     archive.mkdir(exist_ok=True)
        #     shutil.move(str(target / name), str(dest))
        archived += 1

    # 3. Create missing folders with make_cv -b
    failed = []
    for name in sorted(wanted - present):
        print(f"CREATE   {name}")
        if args.dry_run:
            created += 1
            continue
        result = subprocess.run(["make_cv", "-b", name], cwd=target)
        if result.returncode == 0 and (target / name).is_dir():
            write_employee_id(target / name, id_of[name])
            created += 1
        else:
            failed.append(name)

    print(f"\nDone{' (dry run)' if args.dry_run else ''}: "
          f"{created} created, {renamed} renamed, {archived} archived, "
          f"{len(wanted & present) - renamed} already up to date")
    if failed:
        print(f"{len(failed)} folder(s) failed to create:")
        for name in failed:
            print(f"   {name}")
        sys.exit(1)


if __name__ == "__main__":
    main()
