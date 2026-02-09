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
	
# This allows us to either use a proposals file with a Y/N or a separate grants file that has similar columns but no Funded? column
	if not "Funded?" in props.columns:
		props["Funded?"] = "Y"
	props.fillna(value={"Sponsor": "", "Title": "", "Allocated Amt": 0, "Total Cost": 0, "Funded?": "N", "Begin Date": dt.datetime(1900,1,1),"End Date": dt.datetime(1900,1,1)},inplace=True)
	grants = props[props['Funded?'].str.match('Y')]
	
	if years > 0:
		today = date.today()
		year = today.year
		begin_year = year - years	
		grants = grants[grants['End Date'].apply(lambda x: x.year) >= begin_year]
	
	if grants.empty:
		print("No grants found in the last " + str(years) + " years.")
		return(pd.DataFrame())
	
	table = grants.pivot_table(values=['Proposal_ID'], index=['FacultyName'], aggfunc={'Proposal_ID': 'count'},observed=False)
	table.columns=['GCount']
	new_df = table
 
	# creating the bar plot
	fig = plt.figure(figsize = (10, 5))
	plt.bar(table.index, table['GCount'], color ='blue',
			width = 0.4)
	plt.xticks(rotation = 90) # Rotates X-Axis Ticks by 45-degrees
	plt.xlabel("Faculty")
	plt.ylabel("Number of Active Grants")
	plt.savefig('Tables/grant_count.png',bbox_inches='tight',pad_inches=1)
	plt.close()

	table = grants.pivot_table(values=['Allocated Amt'], index=['FacultyName'], aggfunc={'Allocated Amt': 'sum'},observed=False)
	table.columns=['GAmt']
	new_df = pd.concat([new_df, table],axis=1)

	# creating the bar plot
	fig = plt.figure(figsize = (10, 5))
	plt.bar(table.index, table['GAmt'], color ='blue',
			width = 0.4)
	plt.xticks(rotation = 90) # Rotates X-Axis Ticks by 45-degrees
	plt.xlabel("Faculty")
	plt.ylabel("Active Grant Allocation")
	plt.savefig('Tables/grant_amt.png',bbox_inches='tight',pad_inches=1)
	plt.close()
	
	return(new_df)

if __name__ == "__main__":
	main(sys.argv,3)
