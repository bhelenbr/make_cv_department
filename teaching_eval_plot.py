#! /usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
from datetime import date
from make_cv.stringprotect import abbreviate_name

def main(argv,FacultyNames,years,private):
	source = argv[1] # file to read
	try:
		#df = pd.read_excel(source,sheet_name="Data")
		df = pd.read_excel(source)
	except OSError:
		print("Could not open/read file: " + source)
		return(0)
		
	today = date.today()
	year = today.year
	begin_year = year - years
	
	df = df[df['term'].apply(lambda x: int(x[-4:])) >= begin_year]
	
	
	Abbrev = [abbreviate_name(item,first_initial_only=True) for item in FacultyNames]
	FacultyLookup = dict(zip(Abbrev, FacultyNames))
	df['INSTR_NA'] = df['INSTR_NA'].apply(lambda x: abbreviate_name(x,first_initial_only=True))	
	
	# Filter out to only department faculty
	if (len(FacultyNames) > 0):
		df = df[df['INSTR_NA'].isin(Abbrev)]
		df['INSTR_NA'] = df['INSTR_NA'].apply(lambda x: FacultyLookup[x])	
	
	print(FacultyNames)
	print(df)
	table = df.pivot_table(index=['INSTR_NA'],columns=['question'],aggfunc={'enrollment': 'sum','Weighted Average': 'sum', 'count_evals':'sum'})		
	table = table.fillna(0)
	print(table.columns)

	table['q19av'] = np.divide(table[('Weighted Average',19)],table[('count_evals',19)])
	table['q20av'] = np.divide(table[('Weighted Average',20)],table[('count_evals',20)])
	table['q14av'] = np.divide(table[('Weighted Average',14)],table[('count_evals',14)])
	if (private):
		table.sort_values(by=['q19av'], inplace=True,ascending = True)
		table.to_csv('teaching_index.csv', sep=',', encoding='utf-8')
	else:
		table.sort_values(by=['INSTR_NA'], inplace=True,ascending = True)	

	nrows = table.shape[0]
	# creating the bar plot
	x = np.arange(nrows)  # the label locations
	width = 0.25  # the width of the bars
	multiplier = 0

	fig, ax = plt.subplots(layout='constrained')

	for question,data in [("Q14",table['q14av']),("Q19",table['q19av']),("Q20",table['q20av'])]:
		offset = width * multiplier
		rects = ax.bar(x + offset, data, width, label=question)
		#ax.bar_label(rects, padding=3)
		multiplier += 1

	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_ylabel('Weighted Average Teaching Evaluation')
	if (not(private)):
		ax.set_xticks(x + width, table.index)
	ax.legend(loc='upper left', ncols=2)
	plt.xticks(rotation = 90) # Rotates X-Axis Ticks by 45-degrees
	plt.xlabel("Faculty")
	plt.savefig('Tables/teaching_averages.png',bbox_inches='tight',pad_inches=1)
	plt.close()
	
if __name__ == "__main__":
	FacultyNames = ["Achuthan, Ajit","Fite, Kevin","Mastorakos, Ioannis"]
	main(sys.argv,FacultyNames,1,False)