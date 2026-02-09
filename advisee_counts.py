#! /usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
from datetime import date
from make_cv.stringprotect import abbreviate_name

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

	Abbrev = [abbreviate_name(item,first_initial_only=True) for item in FacultyNames]
	FacultyLookup = dict(zip(Abbrev, FacultyNames))
	df['Advisor Name'] = df['Advisor Name'].apply(lambda x : abbreviate_name(x,first_initial_only=True))

	# Filter out to only department faculty
	if (len(FacultyNames) > 0):
		df = df[df['Advisor Name'].isin(Abbrev)]
		df['Advisor Name'] = df['Advisor Name'].apply(lambda x: FacultyLookup[x])
	
	counts = df.groupby(['Advisor Name'])['Count Distinct Name'].sum().to_frame(name='Advisees')
	
	x = np.arange(counts.shape[0])  # the label locations
	width = 0.5  # the width of the bars
	fig, ax = plt.subplots(layout='constrained')
	rects = ax.bar(x, counts['Advisees'], width)

	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_ylabel('Number of Advisees')
	ax.set_xticks(x, counts.index)
	plt.xticks(rotation = 90) # Rotates X-Axis Ticks by 45-degrees
	plt.savefig('Tables/advisee_count.png',bbox_inches='tight',pad_inches=1)
	plt.close()
	
	return(counts)
	
if __name__ == "__main__":
	FacultyNames = ["Achuthan, Ajit","Fite, Kevin","Mastorakos, Ioannis"]
	main(sys.argv,FacultyNames,1)