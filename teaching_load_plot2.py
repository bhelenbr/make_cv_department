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
		#df = pd.read_excel(source,sheet_name="Data")
		df = pd.read_excel(source,dtype={'course_section': str})
	except OSError:
		print("Could not open/read file: " + source)
		return(0)
		
	today = date.today()
	year = today.year
	begin_year = year - years
	
	# STRM, term, school, course, course_num, course_section, course_title, INSTR_NA, ID, count_evals, enrollment, Particip, question, a1, a1_pct, a2, a2_pct, a3, a3_pct, a4, a4_pct, a5, a5_pct, na, na_pct, Calculated Mean, Question, combined_course_num, Weighted Average, FacultyName"
	df = df[df['term'].apply(lambda x: int(x[-4:])) >= begin_year]
		
	# Filter out to only department faculty
	if (len(FacultyNames) > 0):
		df = df[df['FacultyName'].isin(FacultyNames)]
	
	df = df[df['question'] == 1]

	# Merge distance sections with section 01
	df['course_section'] = df['course_section'].apply(lambda x: x.replace('D','0')[0:2])
	df.fillna(value={'enrollment':0},inplace=True)
	
	# Get only lecture sections
	# lectures = df[df['Component'].apply(lambda x: x == 'LEC')]	
	#others = df[df['Component'].apply(lambda x: not(x == 'LEC'))]
	lectures = df

	# Step 1: Aggregate enrollment per section
	sections = lectures.groupby(['FacultyName', 'term', 'combined_course_num', 'course_section'],as_index=False)['enrollment'].sum()
	# Step 2: Count sections per PI
	section_counts = sections['FacultyName'].value_counts().to_frame(name='Sections Taught').sort_index()
	new_df = section_counts
	
	# Step 1: Aggregate enrollment per class
	classes = lectures.groupby(['FacultyName', 'term', 'combined_course_num'],as_index=False)['enrollment'].sum()
	# Step 2: Count sections per PI
	class_counts = classes['FacultyName'].value_counts().to_frame(name='Classes Taught').sort_index()
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
	
	enrollments = lectures.pivot_table(index=['FacultyName'],aggfunc={'enrollment': 'sum'})
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