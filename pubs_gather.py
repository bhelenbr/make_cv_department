#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# Creates excel file with all entries of type
# ../Scripts/pubs_gather.py journal
# ../Scripts/pubs_gather.py invited
# ../Scripts/pubs_gather.py patent
# ../Scripts/pubs_gather.py referreed
# ../Scripts/pubs_gather.py conference
# ../Scripts/pubs_gather.py books


import os, sys, platform
from pathlib import Path
import bibtexparser
import pandas as pd

from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
#from bibtexparser.customization import convert_to_unicode
from bibtexparser.bparser import BibTexParser

def extract_by_keyword(database,keyword):
	bib_database = BibDatabase()
	for icpbe, paperbibentry in enumerate(database.entries):
		if "keywords" in paperbibentry.keys():
			kword = str(paperbibentry["keywords"])
			if kword.find(keyword) > -1:
				bib_database.entries.append(paperbibentry)
	return(bib_database)

# Source is faculty folder
file_source = sys.argv[1]

folder = "Scholarship"
keyword = sys.argv[2]

writer = BibTexWriter()
writer.order_entries_by = None

articles = BibDatabase()
for FacultyName in os.listdir(file_source): # For each faculty member
	if FacultyName.find(",") > -1 and Path(os.path.join(file_source, FacultyName)).is_dir():
		try:
			with open(file_source +os.sep +FacultyName+os.sep+folder +os.sep +"scholarship.bib") as bibtex_file:
				tbparser = BibTexParser(common_strings=True)
				tbparser.homogenize_fields = False  # no dice
				tbparser.alt_dict['url'] = 'url'    # this finally prevents change 'url' to 'link'
				bib_database = bibtexparser.load(bibtex_file,tbparser)
			extract = extract_by_keyword(bib_database,keyword)
			print(FacultyName +" " +str(len(extract.entries)))
			for icpbe, paperbibentry in enumerate(extract.entries):
				paperbibentry["Owner"] = FacultyName
				articles.entries.append(paperbibentry)
		except FileNotFoundError as e:
			print("Could not read file",FacultyName)


sheet = pd.DataFrame(articles.entries)
sheet.to_excel(keyword +".xlsx", index=False)