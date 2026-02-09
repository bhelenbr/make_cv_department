#! /usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
from datetime import date

def main(argv,years):
	source = argv[1] # file to read
	try:
		df = pd.read_excel(source,header=0)
	except OSError:
		print("Could not open/read file: " + source)
		sys.exit()

	if df.empty:
		print("No data available in file: " + source)
		return(df)
	
	today = date.today()
	year = today.year
	begin_year = year - years

	df = df[(df['Year'] >= begin_year)]
	df = df.reset_index()
	if df.empty:
		print("No theses found in the last " + str(years) + " years.")
		return(pd.DataFrame())

	table = df.pivot_table(values=['Student'], index=['FacultyName'], columns=['Degree'], aggfunc={'Student': 'count'},observed=False,fill_value=0)

	x = np.arange(table.shape[0])  # the label locations
	width = 0.25  # the width of the bars
	multiplier = 0

	fig, ax = plt.subplots(layout='constrained')

	table.columns = table.columns.get_level_values('Degree')
	for program in table.columns:
		offset = width * multiplier
		rects = ax.bar(x + offset, table[program], width, label=program)
		#ax.bar_label(rects, padding=3)
		multiplier += 1

	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_ylabel('Theses')
	ax.set_xticks(x + width, table.index)
	ax.legend(loc='upper left', ncols=len(table.columns))
	plt.xticks(rotation = 90) # Rotates X-Axis Ticks by 45-degrees
	plt.savefig('Tables/thesis.png',bbox_inches='tight',pad_inches=1)
	plt.close()


	return(table)

if __name__ == "__main__":
	main(sys.argv,3)