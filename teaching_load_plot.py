#! /usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
from datetime import date
from make_cv.stringprotect import abbreviate_name

def main(argv,FacultyNames,years):
	source = argv[1] # file to read
	try:
		df = pd.read_excel(source,sheet_name="Data")
	except OSError:
		print("Could not open/read file: " + source)
		return(0)
	
	today = date.today()
	year = today.year
	twodigityear = year-int(year/100)*100
	# Spring ends in 2, Fall ends in 9
	if ((today.month > 1) & (today.month < 9)):
		semester = 2
	else:
		semester = 9
	term = 4000+ twodigityear*10 +semester
	# beginterm is 3 years before
	begin_term = term -years*10
	
	df = df[df['Term'].apply(lambda x: (x > begin_term) & (x <= term))]
	df.fillna(value={"PI": ""},inplace=True)

	
	Abbrev = [abbreviate_name(item,first_initial_only=True) for item in FacultyNames]
	FacultyLookup = dict(zip(Abbrev, FacultyNames))
	df['PI'] = df['PI'].apply(lambda x : abbreviate_name(x,first_initial_only=True))	
	# Filter out to only department faculty
	if (len(FacultyNames) > 0):
		df = df[df['PI'].isin(Abbrev)]
		df['PI'] = df['PI'].apply(lambda x: FacultyLookup[x])
	
	if df.empty:
		print("No teaching records found in the last " + str(years) + " years.")
		return(pd.DataFrame())
	
	# Merge distance sections with section 01
	df['Section'] = df['Section'].apply(lambda x: x.replace('D','0')[0:2])
	df.fillna(value={'Enrollment':0},inplace=True)
	

	# Get only lecture sections
	lectures = df[df['Component'].apply(lambda x: x == 'LEC')]	
	#others = df[df['Component'].apply(lambda x: not(x == 'LEC'))]
		

	# Step 1: Aggregate enrollment per section
	sections = lectures.groupby(['PI', 'Term', 'Course Nbr', 'Section'],as_index=False)['Enrollment'].sum()
	# Step 2: Count sections per PI
	section_counts = sections['PI'].value_counts().to_frame(name='Sections Taught').sort_index()
	new_df = section_counts
	
	# Step 1: Aggregate enrollment per class
	classes = lectures.groupby(['PI', 'Term', 'Course Nbr'],as_index=False)['Enrollment'].sum()
	# Step 2: Count sections per PI
	class_counts = classes['PI'].value_counts().to_frame(name='Classes Taught').sort_index()
	new_df = pd.concat([new_df, class_counts],axis=1)

	x = np.arange(section_counts.shape[0])  # the label locations
	width = 0.25  # the width of the bars
	multiplier = 0

	fig, ax = plt.subplots(layout='constrained')
	offset = width * multiplier
	rects = ax.bar(x + offset, section_counts['Sections Taught'], width, label='sections')
	multiplier += 1
	offset = width * multiplier
	rects = ax.bar(x + offset, class_counts['Classes Taught'], width, label='classes')
	multiplier += 1	
	
	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_ylabel('Sections / Classes Taught')
	ax.set_xticks(x+width/2, section_counts.index)
	#ax.set_yticks(range(20))
	ax.legend(loc='upper left', ncols=2)
	plt.xticks(rotation = 90) # Rotates X-Axis Ticks by 45-degrees
	plt.savefig('Tables/teaching_counts.png',bbox_inches='tight',pad_inches=1)
	plt.close()
	
	enrollments = lectures.pivot_table(index=['PI'],aggfunc={'Enrollment': 'sum'})
	enrollments.columns=['Enrollment']
	new_df = pd.concat([new_df, enrollments],axis=1)

	x = np.arange(enrollments.shape[0])  # the label locations
	width = 0.25  # the width of the bars
	fig, ax = plt.subplots(layout='constrained')
	rects = ax.bar(x, enrollments['Enrollment'], width, label='Enrollment')

	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_ylabel('Students Taught')
	ax.set_xticks(x, enrollments.index)
	plt.xticks(rotation = 90) # Rotates X-Axis Ticks by 45-degrees
	plt.savefig('Tables/class_enrollments.png',bbox_inches='tight',pad_inches=1)
	plt.close()
	
	return(new_df)
	
if __name__ == "__main__":
	FacultyNames = ["Achuthan, Ajit","Fite, Kevin","Mastorakos, Ioannis"]
	main(sys.argv,FacultyNames,3)