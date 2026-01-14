#! /usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
from datetime import date

from merge_df import merge_and_dedup

def main(argv,years):
	source = argv[1] # file to read
	try:
		df = pd.read_excel(source,header=0)
	except OSError:
		print("Could not open/read file: " + source)
		sys.exit()
	
	today = date.today()
	year = today.year
	begin_year = year - years

	df = df[(df['Calendar Year'] >= begin_year)]
	df = df.reset_index()
	
	professional = df[(df['Type'] == 'Professional')]
	community = df[(df['Type'] == 'Community')]
	university = df[(df['Type'] == 'University') | (df['Type'] == 'Department')]
	
	if not professional.empty:
		table_prof = professional.pivot_table(values=['Hours/Semester'], index=['FacultyName'], aggfunc={'Hours/Semester': 'sum'},observed=False)
		table_prof.columns=['Prof. Service']

		# creating the bar plot
		fig = plt.figure(figsize = (10, 5))
		plt.bar(table_prof.index, table_prof['Prof. Service'], color ='blue',width = 0.4)
		plt.xticks(rotation = 90) # Rotates X-Axis Ticks by 45-degrees
		plt.xlabel("Faculty")
		plt.ylabel("Professional Service Hours")
		plt.ylim([0,300])
		plt.savefig('Tables/professional_service.png',bbox_inches='tight',pad_inches=1)
		plt.close()
	else:
		table_prof = pd.DataFrame()
	
	if not community.empty:
		table_com = community.pivot_table(values=['Hours/Semester'], index=['FacultyName'], aggfunc={'Hours/Semester': 'sum'},observed=False)
		table_com.columns=['Comm. Service']

		# creating the bar plot
		fig = plt.figure(figsize = (10, 5))
		plt.bar(table_com.index, table_com['Comm. Service'], color ='blue',width = 0.4)
		plt.xticks(rotation = 90) # Rotates X-Axis Ticks by 45-degrees
		plt.xlabel("Faculty")
		plt.ylabel("Community Service Hours")
		plt.savefig('Tables/community_service.png',bbox_inches='tight',pad_inches=1)
		plt.close()
	else:
		table_com = pd.DataFrame()
	
	if not university.empty:
		table_univ = university.pivot_table(values=['Hours/Semester'], index=['FacultyName'], aggfunc={'Hours/Semester': 'sum'},observed=False)
		table_univ.columns=['U. Service']

		# creating the bar plot
		fig = plt.figure(figsize = (10, 5))
		plt.bar(table_univ.index, table_univ['U. Service'], color ='blue',width = 0.4)
		plt.xticks(rotation = 90) # Rotates X-Axis Ticks by 45-degrees
		plt.xlabel("Faculty")
		plt.ylabel("University Service Hours")
		plt.ylim([0,1000])
		plt.savefig('Tables/university_service.png',bbox_inches='tight',pad_inches=1)
		plt.close()
	else:
		table_univ = pd.DataFrame()

	
	new_df = merge_and_dedup([table_prof,table_com,table_univ])
	return(new_df)
	
if __name__ == "__main__":
	main(sys.argv,3)