#!/usr/bin/python3

# Python code to scatter file to faculty folder
# First argument is file to scatter, second argument is Faculty folder, third argument is subfolder name i.e.
# scatter <file to scatter> <Faculty folder> <Subfolder>\\


import os
import shutil
import sys
import platform
from pathlib import Path

# Destination is faculty folder
if platform.system() == 'Windows':
	file_destination = r"S:\departments\Mechanical & Aeronautical Engineering\Faculty"
else:
	file_destination = r"/Volumes/Mechanical & Aerospace Engineering/Faculty"
    
# Graphically select file to scatter
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
root = tk.Tk()
root.withdraw()
source = filedialog.askopenfilename(title='Select file to scatter to Faculty directories')

# Graphically ask for subfolder name
subfolder = tk.simpledialog.askstring('Name of Subfolder', 'Type name')

print(subfolder)
base_path = Path(file_destination)
for faculty_dir in base_path.iterdir(): # For each faculty member
	if not faculty_dir.is_dir() or faculty_dir.name.startswith('.'):
		continue
	subfolder_path = faculty_dir / subfolder
	try:
		existing = [p.name for p in subfolder_path.iterdir()]
	except Exception:
		existing = []
	if os.path.basename(source) not in existing:
		subfolder_path.mkdir(parents=True, exist_ok=True)
		shutil.copy(source, subfolder_path)

