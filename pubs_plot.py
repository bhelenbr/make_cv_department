#! /usr/bin/env python3

import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
from datetime import date

def main(argv,years):
	new_df = pd.DataFrame();

	for name in ['journal','refereed','patent','conference','book','invited']:
		source = argv[1] +os.sep +name +".xlsx"
		try:
			df = pd.read_excel(source)
		except OSError:
			print("Could not open/read file: " + source)
			continue

		if (df.empty):
			continue

		today = date.today()
		year = today.year
		begin_year = year - years
		

		df = df[(df['year'] >= begin_year)]
		df = df.reset_index()
		if (df.shape[0] > 0):
			table = df.pivot_table(values=['ID'], index=['Owner'], aggfunc={'ID': 'count'},observed=False)
			table.columns=[name]

			# creating the bar plot
			fig = plt.figure(figsize = (10, 5))
			plt.bar(table.index, table[name], color ='blue',
					width = 0.4)
			plt.xticks(rotation = 90) # Rotates X-Axis Ticks by 45-degrees
			plt.xlabel("Faculty")
			plt.ylabel("Count")
			plt.savefig('Tables' +os.sep +name +'.png',bbox_inches='tight',pad_inches=1)
			plt.close()
			new_df = pd.concat([new_df, table],axis=1)
	
	return(new_df)

if __name__ == "__main__":
	main(sys.argv,3)