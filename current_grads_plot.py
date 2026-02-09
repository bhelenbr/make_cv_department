#! /usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
from datetime import date

def main(argv):
	source = argv[1] # file to read
	try:
		df = pd.read_excel(source,header=0)
	except OSError:
		print("Could not open/read file: " + source)
		return(pd.DataFrame())
	
	df['Current Program'] = df['Current Program'].apply(lambda x: x[(x.find("-")+1):] if isinstance(x, str) else "MS")
	table = df.pivot_table(values=['Student Name'], index=['FacultyName'], columns=['Current Program'], aggfunc={'Student Name': 'count'},observed=False,fill_value=0)
	if table.empty:
		print("No graduate advisees found in file: " + source)
		return(pd.DataFrame())
	
	# Simplify the multindex column names
	table = table['Student Name']
	

	x = np.arange(table.shape[0])  # the label locations
	width = 0.25  # the width of the bars
	multiplier = 0

	fig, ax = plt.subplots(layout='constrained')

	for program in table.columns:
		offset = width * multiplier
		rects = ax.bar(x + offset, table[program], width, label=program)
		#ax.bar_label(rects, padding=3)
		multiplier += 1

	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_ylabel('Graduate Advisees')
	ax.set_xticks(x + width, table.index)
	ax.legend(loc='upper left', ncols=2)
	plt.xticks(rotation = 90) # Rotates X-Axis Ticks by 45-degrees
	plt.savefig('Tables/graduate_advisees.png',bbox_inches='tight',pad_inches=1)
	plt.close()
	
	#table.columns=['MS Advisees','PhD Advisees']
	return(table)
	
if __name__ == "__main__":
	main(sys.argv)