#! /usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
from datetime import date
import datetime as dt

def main(argv,years):
	source = argv[1] # file to read
	try:
		props = pd.read_excel(source,header=0)
	except OSError:
		print("Could not open/read file: " + source)
		sys.exit()
	
	today = date.today()
	year = today.year
	begin_year = year - years

	if years > 0:
		today = dt.date.today()
		year = today.year
		begin_year = year - years
		# Use vectorized access to the year to avoid invalid comparisons
		mask = props['Submit Date'].dt.year >= begin_year
		props = props[mask.fillna(False)]

	table = props.pivot_table(values=['Proposal_ID'], index=['FacultyName'], aggfunc={'Proposal_ID': 'count'},observed=False)

	table.columns=['PCount']
	
	new_df = table
 
	# creating the bar plot
	fig = plt.figure(figsize = (10, 5))
	plt.bar(table.index, table['PCount'], color ='blue',
			width = 0.4)
	plt.xticks(rotation = 90) # Rotates X-Axis Ticks by 45-degrees
	plt.xlabel("Faculty")
	plt.ylabel("Proposals Submitted")
	plt.savefig('Tables/proposal_count.png',bbox_inches='tight',pad_inches=1)
	plt.close()
	
	table = props.pivot_table(values=['Allocated Amt'], index=['FacultyName'], aggfunc={'Allocated Amt': 'sum'},observed=False)
	table.columns=['PAmt']
	
	new_df = pd.concat([new_df, table],axis=1)

	# creating the bar plot
	fig = plt.figure(figsize = (10, 5))
	plt.bar(table.index, table['PAmt'], color ='blue',
			width = 0.4)
	plt.xticks(rotation = 90) # Rotates X-Axis Ticks by 45-degrees
	plt.xlabel("Faculty")
	plt.ylabel("Proposal Amount Allocation")
	plt.savefig('Tables/proposal_amt.png',bbox_inches='tight',pad_inches=1)
	plt.close()

	props = props[props['Funded?'].str.match('Y')]
	table = props.pivot_table(values=['Proposal_ID'], index=['FacultyName'], aggfunc={'Proposal_ID': 'count'},observed=False)
	table.columns=['GCount']
	new_df = pd.concat([new_df, table],axis=1)
 
	# creating the bar plot
	fig = plt.figure(figsize = (10, 5))
	plt.bar(table.index, table['GCount'], color ='blue',
			width = 0.4)
	plt.xticks(rotation = 90) # Rotates X-Axis Ticks by 45-degrees
	plt.xlabel("Faculty")
	plt.ylabel("Proposals Funded")
	plt.savefig('Tables/grant_count.png',bbox_inches='tight',pad_inches=1)
	plt.close()

	table = props.pivot_table(values=['Allocated Amt'], index=['FacultyName'], aggfunc={'Allocated Amt': 'sum'},observed=False)
	table.columns=['GAmt']
	new_df = pd.concat([new_df, table],axis=1)

	# creating the bar plot
	fig = plt.figure(figsize = (10, 5))
	plt.bar(table.index, table['GAmt'], color ='blue',
			width = 0.4)
	plt.xticks(rotation = 90) # Rotates X-Axis Ticks by 45-degrees
	plt.xlabel("Faculty")
	plt.ylabel("Grants Amount Allocation")
	plt.savefig('Tables/grant_amt.png',bbox_inches='tight',pad_inches=1)
	plt.close()
	
	return(new_df)

if __name__ == "__main__":
	main(sys.argv,3)