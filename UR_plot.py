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
	
	today = date.today()
	year = today.year
	begin_year = year - years

	df = df[(df['Calendar Year'] >= begin_year)]
	if df.empty:
		print("No undergraduate research projects found in the last " + str(years) + " years.")
		return(pd.DataFrame())
	
	df.sort_values(by=['Calendar Year','Term'], inplace=True, ascending = [False,True])
	df = df.reset_index()

	table = df.pivot_table(values=['Students'], index=['FacultyName'], aggfunc={'Students': 'count'},observed=False)
	table.columns=['URCount']
 
	# creating the bar plot
	fig = plt.figure(figsize = (10, 5))
	plt.bar(table.index, table['URCount'], color ='blue',
			width = 0.4)
	plt.xticks(rotation = 90) # Rotates X-Axis Ticks by 45-degrees
	plt.xlabel("Faculty")
	plt.ylabel("Undergraduate Projects Advised")
	plt.savefig('Tables/UR.png',bbox_inches='tight',pad_inches=1)
	plt.close()
	
	return(table)

if __name__ == "__main__":
	main(sys.argv,3)