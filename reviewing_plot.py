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
		return(pd.DataFrame())
	
	today = date.today()
	year = today.year
	begin_year = year - years

	df = df[(df['Start'].apply(lambda x: x.year) >= begin_year)]
	df = df.reset_index()
	if df.empty:
		print("No reviews found in the last " + str(years) + " years.")
		return(pd.DataFrame())

	table = df.pivot_table(values=['Rounds'], index=['FacultyName'], aggfunc={'Rounds': 'sum'},observed=False)
	table.columns=['Reviews']
 
	# creating the bar plot
	fig = plt.figure(figsize = (10, 5))
	plt.bar(table.index, table['Reviews'], color ='blue',
			width = 0.4)
	plt.xticks(rotation = 90) # Rotates X-Axis Ticks by 45-degrees
	plt.xlabel("Faculty")
	plt.ylabel("Number of Reviews")
	plt.savefig('Tables/reviews.png',bbox_inches='tight',pad_inches=1)
	plt.close()
	
	return(table)
	
if __name__ == "__main__":
	main(sys.argv,3)