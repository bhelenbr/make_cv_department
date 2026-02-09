#! /usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
from datetime import date

def main(argv,FacultyNames,years):
	source = argv[1] # file to read
	try:
		df = pd.read_excel(source,header=0)
	except OSError:
		print("Could not open/read file: " + source)
		sys.exit()
	
	today = date.today()
	year = today.year
	begin_year = year - years
	
	df = df[(df['Date'].apply(lambda x: x.year) >= begin_year)]
	df.columns = ['Date','Time','StudentName','Area','FacultyName','Place','Notes']
	df.fillna(value={"FacultyName": "Professor No-one"},inplace=True)
	df['FacultyName'] = df['FacultyName'].apply(lambda x: x[(x.find(' ')+1):].strip())
	
	
	LastNames = [x[:x.find(',')] for x in FacultyNames]
	FacultyLookup = dict(zip(LastNames, FacultyNames))

	# Filter out to only department faculty
	if (len(FacultyNames) > 0):
		df = df[df['FacultyName'].isin(LastNames)]
		df['FacultyName'] = df['FacultyName'].apply(lambda x: FacultyLookup[x])
	
	table = df.pivot_table(index=['FacultyName'], aggfunc={'StudentName': 'count'})
	table.columns=['Prosp. Visits']
 
	# creating the bar plot
	fig = plt.figure(figsize = (10, 5))
	plt.bar(table.index, table['Prosp. Visits'], color ='blue',
			width = 0.4)
	plt.xticks(rotation = 90) # Rotates X-Axis Ticks by 45-degrees
	plt.xlabel("Faculty")
	plt.ylabel("Student Visits")
	plt.savefig('Tables/visits.png',bbox_inches='tight',pad_inches=1)
	plt.close()
	
	return(table)

if __name__ == "__main__":
	FacultyNames = ["Achuthan, Ajit","Fite, Kevin","Mastorakos, Ioannis"]
	main(sys.argv,FacultyNames,3)