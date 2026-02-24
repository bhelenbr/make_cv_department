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
		df = pd.read_excel(source)
	except OSError:
		print("Could not open/read file: " + source)
		return(pd.DataFrame())
	
	today = date.today()
	year = today.year
	begin_year = year - years
	
	#print(df.shape[0])
	df.fillna(0,inplace=True)
	df = df[df['Term'].apply(lambda x: int(x/10)-400+2000) >= begin_year]
	#print(df.shape[0])
	
	Abbrev = [abbreviate_name(item,first_initial_only=True) for item in FacultyNames]
	FacultyLookup = dict(zip(Abbrev, FacultyNames))
	df['LN,FN'] = df['LN,FN'].apply(lambda x: abbreviate_name(x,first_initial_only=True))	
	# Filter out to only department faculty
	if (len(FacultyNames) > 0):
		df = df[df['LN,FN'].isin(Abbrev)]
		df['LN,FN'] = df['LN,FN'].apply(lambda x: FacultyLookup[x])
		
	df['Sum of Responses'] = df['Question 0'] + df['Question 1'] + df['Question 2'] + df['Question 3'] + df['Question 4'] + df['Question 5']
	df['Total Points'] = df['Question 1'] + 2*df['Question 2'] + 3*df['Question 3'] + 4*df['Question 4'] + 5*df['Question 5']
		

	
	table = df.pivot_table(index=['LN,FN'],columns=['Number'],aggfunc={'Sum of Responses': 'sum','Total Points': 'sum'})		
	if table.empty:
		print("No advising evaluations found in the last " + str(years) + " years.")
		return(pd.DataFrame())
	
	fig, ax = plt.subplots(layout='constrained')
	for count,faculty in enumerate(table.index):
		responses = []
		for question in range(1,12):
			responses.append(table.loc[faculty,('Total Points',question)]/table.loc[faculty,('Sum of Responses',question)])
		ax.plot(range(1,12),responses,label=faculty)
		if (not(private)):
			ax.text(11,table.loc[faculty,('Total Points',11)]/table.loc[faculty,('Sum of Responses',11)],faculty,fontsize='xx-small')
	#ax.legend(fontsize='xx-small',ncols=2)
	ax.set_ylabel('Average Score')
	ax.set_xlabel('Question #')
	plt.xlim([1,15])
	plt.savefig('Tables/advising_averages.png',bbox_inches='tight',pad_inches=1)
	plt.close()
	
	table['avg11'] = np.divide(table[('Total Points',11)],table[('Sum of Responses',11)])
	if (private):
		table.sort_values(by=['avg11'], inplace=True,ascending = True)
		table.index.to_series().to_csv('advising_index.csv', index=False, header=False, encoding='utf-8')
	
	x = np.arange(table.shape[0])  # the label locations
	width = 0.25  # the width of the bars
	multiplier = 0
	fig, ax = plt.subplots(layout='constrained')
	for question in [5,11]:
		offset = width * multiplier
		rects = ax.bar(x + offset, np.divide(table[('Total Points',question)],table[('Sum of Responses',question)]), width, label=str(question))
		multiplier += 1
	ax.bar_label(rects, padding=3,labels=table[('Sum of Responses',11)].apply(lambda x: int(x)))

	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_ylabel('Average Score')
	ax.set_ylim([3,5])
	if (not(private)):
		ax.set_xticks(x + width, table.index)
	ax.legend(loc='upper left', ncols=2)
	plt.xticks(rotation = 90) # Rotates X-Axis Ticks by 45-degrees
	plt.savefig('Tables/advising5_11.png',bbox_inches='tight',pad_inches=1)
	plt.close()
	
	df = table['avg11']
	return(df)
	
if __name__ == "__main__":
	FacultyNames = ["Achuthan, Ajit","Fite, Kevin","Mastorakos, Ioannis"]
	main(sys.argv,FacultyNames,3,False)