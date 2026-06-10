#! /usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
from datetime import date
from make_cv.stringprotect import abbreviate_name

# STRM	term	course_num	course_section	combined_course_num	combined_num_sec	course_title	component	mode	role	enrollment	count_1	mean_1	count_2	mean_2	count_3	mean_3	count_4	mean_4	count_5	mean_5	count_6	mean_6	count_7	mean_7	count_8	mean_8	count_9	mean_9	count_10	mean_10	count_11	mean_11	count_12	mean_12	count_13	mean_13	count_14	mean_14	count_15	mean_15	count_16	mean_16	count_17	mean_17	count_18	mean_18	count_19	mean_19	count_20	mean_20	FacultyName

def main(argv,FacultyNames,years,private):
	source = argv[1] # file to read
	try:
		#df = pd.read_excel(source,sheet_name="Data")
		df = pd.read_excel(source)
	except OSError:
		print("Could not open/read file: " + source)
		return(0)
		
	today = date.today()
	year = today.year
	begin_year = year - years
	
	df = df[df['term'].apply(lambda x: int(x[-4:])) >= begin_year]
	if df.empty:
		print("No teaching evaluations found in the last " + str(years) + " years.")
		return(pd.DataFrame())
	
	Abbrev = [abbreviate_name(item,first_initial_only=True) for item in FacultyNames]
	FacultyLookup = dict(zip(Abbrev, FacultyNames))
	df['FacultyName'] = df['FacultyName'].apply(lambda x: abbreviate_name(x,first_initial_only=True))	
	
	# Filter out to only department faculty
	if (len(FacultyNames) > 0):
		df = df[df['FacultyName'].isin(Abbrev)]
		df['FacultyName'] = df['FacultyName'].apply(lambda x: FacultyLookup[x])	
	
	# components: CLN -clinical DIS-discussion FLD-fieldwork IND-independent study LAB-lab LEC-lecture PHY-physical education PRA-practacum PRO-project RSC-research SEM-seminar THE-thesis TUT-tutorial						
	df = df[~df['component'].isin(['DIS','IND','PRO','RSC','TUT','THE'])]	
	df['weighted_19'] = df['count_19'] * df['mean_19']
	df['weighted_20'] = df['count_20'] * df['mean_20']
	df['weighted_14'] = df['count_14'] * df['mean_14']


	table = df.pivot_table(index=['FacultyName'],aggfunc={'enrollment': 'sum','weighted_14': 'sum','weighted_19': 'sum','weighted_20': 'sum','count_14':'sum','count_19':'sum','count_20':'sum'})		
	table = table.fillna(0)

	if table.empty:
		print("No teaching evaluations found in the last " + str(years) + " years.")
		return(pd.DataFrame())

	table['q19av'] = np.divide(table['weighted_19'],table['count_19'])
	table['q20av'] = np.divide(table['weighted_20'],table['count_20'])
	table['q14av'] = np.divide(table['weighted_14'],table['count_14'])
	if (private):
		table.sort_values(by=['q19av'], inplace=True,ascending = True)
		# Output the ordered list of instructor names (one per line)
		table.index.to_series().to_csv('teaching_index.csv', index=False, header=False, encoding='utf-8')
	else:
		table.sort_values(by=['FacultyName'], inplace=True,ascending = True)	

	nrows = table.shape[0]
	# creating the bar plot
	x = np.arange(nrows)  # the label locations
	width = 0.25  # the width of the bars
	multiplier = 0

	fig, ax = plt.subplots(layout='constrained')

	for question,data in [("Q14",table['q14av']),("Q19",table['q19av']),("Q20",table['q20av'])]:
		offset = width * multiplier
		rects = ax.bar(x + offset, data, width, label=question)
		#ax.bar_label(rects, padding=3)
		multiplier += 1

	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_ylabel('Weighted Average Teaching Evaluation')
	if (not(private)):
		ax.set_xticks(x + width, table.index)
	ax.legend(loc='upper left', ncols=2)
	plt.xticks(rotation = 90) # Rotates X-Axis Ticks by 45-degrees
	plt.xlabel("Faculty")
	plt.savefig('Tables/teaching_averages.png',bbox_inches='tight',pad_inches=1)
	plt.close()
	
if __name__ == "__main__":
	FacultyNames = ["Achuthan, Ajit","Fite, Kevin","Mastorakos, Ioannis"]
	main(sys.argv,FacultyNames,1,False)