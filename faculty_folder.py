"""Helpers for per-faculty folder names.

Folders may be named either "Lastname, Firstname" (old style) or
"Lastname, Firstname - EmployeeID" (created by sync_faculty_folders.py).
"""

import re

# Same convention as sync_faculty_folders.py: " - <id>" at the end of the name
_ID_SUFFIX = re.compile(r"^(.*,.*?)\s+-\s+(\S+)$")


def split_folder_name(folder_name):
	"""Return (display_name, employee_id) for a faculty folder name.

	employee_id is None when the folder has no " - <id>" suffix.
	"""
	name = folder_name.strip()
	m = _ID_SUFFIX.match(name)
	if m:
		return m.group(1).strip(), m.group(2).strip()
	return name, None


def normalize_id(value):
	"""Employee IDs read from Excel can come back as 1234567.0; normalize to a string."""
	if value is None:
		return ""
	s = str(value).strip()
	if s.lower() == "nan":
		return ""
	if s.endswith(".0") and s[:-2].isdigit():
		s = s[:-2]
	return s


def find_faculty_row(df, folder_name, name_col, id_col=None):
	"""Return the rows of df that belong to the faculty folder.

	Matches on the employee ID when the folder name has one and df has id_col;
	otherwise (or if the ID matches nothing) falls back to an exact match of the
	"Lastname, Firstname" part against name_col.
	"""
	display_name, emp_id = split_folder_name(folder_name)
	if emp_id and id_col and id_col in df.columns:
		entries = df[df[id_col].apply(normalize_id) == emp_id]
		if not entries.empty:
			return entries
	return df[df[name_col].astype(str).str.strip() == display_name]


def display_name(folder_name):
	"""Return "Lastname, Firstname" with any " - <id>" suffix removed."""
	return split_folder_name(folder_name)[0]


def display_labels(folder_names):
	"""Return display names for a list of faculty keys (folder names).

	The employee ID is dropped, except where two people in the list would end
	up with the same "Lastname, Firstname"; those keep the ID so they stay distinct.
	"""
	folder_names = [str(n) for n in folder_names]
	names = [display_name(n) for n in folder_names]
	counts = {}
	for n in names:
		counts[n] = counts.get(n, 0) + 1
	return [n if counts[n] == 1 else f for n, f in zip(names, folder_names)]


def match_faculty(values, FacultyNames):
	"""Map each value (a faculty key or a name from university data) to one of
	FacultyNames, or None if there is no unambiguous match.

	Exact matches on the folder name win. Otherwise fall back to matching the
	abbreviated name ("B. Helenbrook"), but only when that abbreviation belongs
	to exactly one faculty folder, so people with the same name are never merged.
	"""
	from make_cv.stringprotect import abbreviate_name
	exact = set(FacultyNames)
	by_abbrev = {}
	for f in FacultyNames:
		by_abbrev.setdefault(abbreviate_name(display_name(f), first_initial_only=True), []).append(f)

	def lookup(v):
		if v is None:
			return None
		v = str(v).strip()
		if v in exact:
			return v
		cands = by_abbrev.get(abbreviate_name(display_name(v), first_initial_only=True), [])
		return cands[0] if len(cands) == 1 else None

	return [lookup(v) for v in values]
