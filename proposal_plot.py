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
		props = pd.read_excel(source,header=0,dtype={'Submit Date': 'datetime64[ns]'})
	except OSError:
		print("Could not open/read file: " + source)
		return(pd.DataFrame())
	
	props.fillna(value={"Sponsor": "", "Title": "", "Allocated Amt": 0, "Total Cost": 0, "Funded?": "N", "Begin Date": dt.datetime(1900,1,1),"End Date": dt.datetime(1900,1,1)},inplace=True)
	# Ensure date columns are real datetimes to avoid pandas downcasting
	props["Submit Date"] = pd.to_datetime(props["Submit Date"], errors='coerce')
	props["Begin Date"] = pd.to_datetime(props["Begin Date"], errors='coerce')
	# Avoid chained-assignment by assigning the filled Series back to the DataFrame
	props["Submit Date"] = props["Submit Date"].fillna(props["Begin Date"])

	
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

	if props.empty:
		print("No proposals found in the last " + str(years) + " years.")
		return(pd.DataFrame())
	
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
	
	return(new_df)

if __name__ == "__main__":
	main(sys.argv,3)
