#! /usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
from datetime import date
from make_cv.stringprotect import abbreviate_name
from faculty_folder import display_labels, match_faculty

def main(argv,FacultyNames,years):
	source = argv[1] # file to read
	try:
		df = pd.read_excel(source,sheet_name="Sheet1")
	except OSError:
		print("Could not open/read file: " + source)
		return(pd.DataFrame())
	
	# Only plot this year
	today = date.today()
	year = int(today.year)
	begin_year = year - years
	df = df[df['YEAR'].apply(lambda x: int(x)) >= begin_year]

	if df.empty:
		print("No advisee records found in the last " + str(years) + " years.")
		return(pd.DataFrame())

	# Filter out to only department faculty.  Advisor Name is the folder name set by
	# advisee_counts_gather.py (may include " - EmployeeID"), so people with the same
	# name stay separate.
	if (len(FacultyNames) > 0):
		df = df.copy()
		df['Advisor Name'] = match_faculty(df['Advisor Name'], FacultyNames)
		df = df[df['Advisor Name'].notna()]
	
	# Advisee counts are snapshots, so use only each advisor's most recent year (don't add years together)
	df = df[df['YEAR'] == df.groupby('Advisor Name')['YEAR'].transform('max')]
	counts = df.groupby(['Advisor Name'])['Count'].sum().to_frame(name='Advisees')

	x = np.arange(counts.shape[0])  # the label locations
	width = 0.5  # the width of the bars
	fig, ax = plt.subplots(layout='constrained')
	rects = ax.bar(x, counts['Advisees'], width)

	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_ylabel('Number of Advisees')
	ax.set_xticks(x, display_labels(counts.index))
	plt.xticks(rotation = 90) # Rotates X-Axis Ticks by 45-degrees
	plt.savefig('Tables/advisee_count.png',bbox_inches='tight',pad_inches=1)
	plt.close()
	
	return(counts)
	
if __name__ == "__main__":
	FacultyNames = ["Achuthan, Ajit","Fite, Kevin","Mastorakos, Ioannis"]
	main(sys.argv,FacultyNames,1)