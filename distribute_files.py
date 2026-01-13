#!/usr/bin/env python3

import os
import shutil
import sys
import platform
from pathlib import Path

# call like this
# distribute_files.py <Folder with files> <Subfolder> <filename>

# inputs
filefolder = sys.argv[1]
subfolder = sys.argv[2]
filename = sys.argv[3]

# Destination is faculty folder
if platform.system() == 'Windows':
	file_destination = r"S:\departments\Mechanical & Aerospace Engineering\Faculty"
else:
	file_destination = r"/Volumes/Mechanical & Aerospace Engineering/Faculty"
    
base_path = Path(file_destination)
for faculty_dir in base_path.iterdir():
	if not faculty_dir.is_dir():
		continue
	FacultyName = faculty_dir.name
	lastname = FacultyName.lower()[0:FacultyName.find(",")];
	print(lastname)
	for fileToMove in os.listdir(filefolder):
		if fileToMove.lower().find(lastname) != -1:
			dest_dir = faculty_dir / subfolder
			dest_dir.mkdir(parents=True, exist_ok=True)
			shutil.copy(Path(filefolder) / fileToMove, dest_dir / fileToMove)
				