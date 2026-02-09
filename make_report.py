#! /usr/bin/env python3

import os
import sys
import glob
import pandas as pd
import platform
import shutil
import openpyxl
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description='This script creates the annual report and assoicated data')
parser.add_argument('-y','--years', type=int, help='The number of years of data to use (default is 1)',default='1')
parser.add_argument('-a','--anonymous', action=argparse.BooleanOptionalAction, help='Anonymize salary & teaching/advising evaluations',default=False)
parser.add_argument('faculty_source', help='Path to faculty data folders')

args = parser.parse_args()
years = args.years
Anonymous_Flag = args.anonymous

# Run this script from the Department Data folder to create annual report
faculty_source = args.faculty_source
gathered_source = ".."

from make_cv.grants2latex_far import grants2latex_far
from make_cv.props2latex_far import props2latex_far
from make_cv.UR2latex_far  import UR2latex_far 
from make_cv.bib2latex_far import bib2latex_far
from make_cv.thesis2latex_far import thesis2latex_far
from make_cv.personal_awards2latex_far import personal_awards2latex_far
from make_cv.student_awards2latex_far import student_awards2latex_far
from make_cv.service2latex_far import service2latex_far
from make_cv.reviews2latex_far import reviews2latex_far
from make_cv.teaching2latex_far import teaching2latex_far

import proposal_plot
import grants_plot
import UR_plot
import pubs_plot
import thesis_plot
import current_grads_plot
import service_plot
import reviewing_plot
import prospective_plot2
import teaching_eval_plot
import teaching_load_plot2
import advising_plot
import advisee_counts


dest_dir = Path("Tables")
  # Ensure destination directory exists
dest_dir.mkdir(parents=False, exist_ok=True)

try:
	files = glob.glob('Tables/*')
	for f in files:
		os.remove(f)
except:
	pass

# Get list of last names
names = sorted(os.listdir(faculty_source), key=str.lower)
FacultyNames = []
for name in names:
	if name.find(",") > -1 and Path(faculty_source,name).is_dir():
		FacultyNames.append(name)	

df = pd.DataFrame();

new_df = proposal_plot.main(['proposal_plot',gathered_source +os.sep +"Proposals & Grants" +os.sep +'proposals & grants.xlsx'],years)
df = pd.concat([df, new_df],axis=1)
new_df = grants_plot.main(['grants_plot',gathered_source +os.sep +"Proposals & Grants" +os.sep +'grants.xlsx'],years)
df = pd.concat([df, new_df],axis=1)
new_df = UR_plot.main(['UR_plot',gathered_source +os.sep +"Service" +os.sep +'undergraduate research data.xlsx'],years)
df = pd.concat([df, new_df],axis=1)
new_df = pubs_plot.main(['pubs_plot',gathered_source +os.sep +"Scholarship"],years)
df = pd.concat([df, new_df],axis=1)
new_df = thesis_plot.main(['thesis_plot',gathered_source +os.sep +"Scholarship" +os.sep +'thesis data.xlsx'],years)
df = pd.concat([df, new_df],axis=1)
new_df = current_grads_plot.main(['current_grad_plot',gathered_source +os.sep +"Scholarship" +os.sep +'current student data.xlsx'])
df = pd.concat([df, new_df],axis=1)
new_df = service_plot.main(['service_plot',gathered_source +os.sep +"Service" +os.sep +'service data.xlsx'],years)
df = pd.concat([df, new_df],axis=1)
new_df = reviewing_plot.main(['reviewing_plot',gathered_source +os.sep +"Service" +os.sep +'reviews data.xlsx'],years)
df = pd.concat([df, new_df],axis=1)
new_df = prospective_plot2.main(['prospective_plot',gathered_source +os.sep +"Service" +os.sep +'prospective visit data.xlsx'],FacultyNames,years)
df = pd.concat([df, new_df],axis=1)
new_df = teaching_eval_plot.main(['teaching_eval_plot',gathered_source +os.sep +"Teaching" +os.sep +'teaching evaluation data.xlsx'],FacultyNames,years,Anonymous_Flag)
df = pd.concat([df, new_df],axis=1)
new_df = teaching_load_plot2.main(['teaching_load_plot',gathered_source +os.sep +"Teaching" +os.sep +'teaching evaluation data.xlsx'],FacultyNames,years)
df = pd.concat([df, new_df],axis=1)
new_df = advising_plot.main(['advising_plot',gathered_source +os.sep +"Service" +os.sep +'advising evaluation data.xlsx'],FacultyNames,years,Anonymous_Flag)
df = pd.concat([df, new_df],axis=1)
new_df = advisee_counts.main(['advisee_counts',gathered_source +os.sep +"Service" +os.sep +'advisee counts.xlsx'],FacultyNames,years)
df = pd.concat([df, new_df],axis=1)
df.to_excel('faculty_data.xlsx')

# open files
fgrants = open('Tables/grants_far.tex', 'a') # file to write
fprops = open('Tables/props_far.tex', 'a') # file to write
fur = open('Tables/UR_far.tex', 'a') # file to write
pubfiles = ["journal_far.tex","conference_far.tex","patent_far.tex","book_far.tex","invited_far.tex","refereed_far.tex","arXiv_far.tex"]
pub_categories = ['Journal','Conference','Patent','Book','Invited','Refereed','arXiv']

fpubs = [open('Tables' +os.sep +name, 'a') for name in pubfiles]
fthesis = open('Tables/thesis_far.tex', 'a') # file to write
fpawards = open('Tables/personal_awards_far.tex', 'a') # file to write
fsawards = open('Tables/student_awards_far.tex', 'a') # file to write
fservice = open('Tables/service_far.tex', 'a') # file to write
freviews = open('Tables/reviews_far.tex', 'a') # file to write
fteaching = open('Tables/teaching_far.tex', 'a') # file to write


br = open('Tables/bibresource.tex','w')
for FacultyName in FacultyNames: # For each faculty member
	print(FacultyName)
	headerstring = '\n\\vspace{\\baselineskip}\n{\\bf ' +FacultyName +'}\n'
	
	# Grants
	filename = faculty_source +os.sep +FacultyName +os.sep +"Proposals & Grants" +os.sep +"grants.xlsx"
	pos = fgrants.tell()
	fgrants.write(headerstring)
	nrows = grants2latex_far(fgrants,years,filename)
	if not(nrows):
		fgrants.seek(pos)
		fgrants.truncate()

	# Proposals
	filename = faculty_source +os.sep +FacultyName +os.sep +"Proposals & Grants" +os.sep +"proposals & grants.xlsx"
	pos = fprops.tell()
	fprops.write(headerstring)
	nrows = props2latex_far(fprops,years,filename)	
	if not(nrows):
		fprops.seek(pos)
		fprops.truncate()
		
	# Undergraduate Research
	filename = faculty_source +os.sep +FacultyName +os.sep +"Service" +os.sep +'undergraduate research data.xlsx'
	pos = fur.tell()
	fur.write(headerstring)
	nrows = UR2latex_far(fur,years,filename)	
	if not(nrows):
		fur.seek(pos)
		fur.truncate()
		
	# Scholarly Works
	filename = faculty_source +os.sep +FacultyName +os.sep +"Scholarship" +os.sep +'scholarship.bib'
	nrecords = [0 for counter in range(len(pubfiles))]
	if os.path.isfile(filename):
		ppos = [fpubs[counter].tell() for counter in range(len(pubfiles))]
		for counter in range(len(pubfiles)):
			fpubs[counter].write(headerstring)
			nrecords[counter] = bib2latex_far(fpubs[counter],filename,[pub_categories[counter]],years=years)
		for counter in range(len(pubfiles)):
			if not(nrecords[counter]):
				fpubs[counter].seek(ppos[counter])
				fpubs[counter].truncate()
		br.write('\\addbibresource{' +filename +'}\n')
	
	# Thesis Publications & Graduate Advisees
	filename1 = faculty_source +os.sep +FacultyName +os.sep +"Scholarship" +os.sep +'current student data.xlsx'
	filename2 = faculty_source +os.sep +FacultyName +os.sep +"Scholarship" +os.sep +'thesis data.xlsx'
	pos = fthesis.tell()
	fthesis.write(headerstring)
	nrows = thesis2latex_far(fthesis,years,filename1,filename2)	
	if not(nrows):
		fthesis.seek(pos)
		fthesis.truncate()	
	
	# Personal Awards
	filename = faculty_source +os.sep +FacultyName +os.sep +"Awards" +os.sep +'personal awards data.xlsx'
	pos = fpawards.tell()
	fpawards.write(headerstring)
	nrows = personal_awards2latex_far(fpawards,years,filename)	
	if not(nrows):
		fpawards.seek(pos)
		fpawards.truncate()	
	
	# Student Awards
	filename = faculty_source +os.sep +FacultyName +os.sep +"Awards" +os.sep +'student awards data.xlsx'
	pos = fsawards.tell()
	fsawards.write(headerstring)
	nrows = student_awards2latex_far(fsawards,years,filename)	
	if not(nrows):
		fsawards.seek(pos)
		fsawards.truncate()			

	# Service Activities
	filename = faculty_source +os.sep +FacultyName +os.sep +"Service" +os.sep +'service data.xlsx'
	pos = fservice.tell()
	fservice.write(headerstring)
	nrows = service2latex_far(fservice,years,filename)	
	if not(nrows):
		fservice.seek(pos)
		fservice.truncate()
	
	# Reviewing Activities
	filename = faculty_source +os.sep +FacultyName +os.sep +"Service" +os.sep +'reviews data.xlsx'
	pos = freviews.tell()
	freviews.write(headerstring)
	nrows = reviews2latex_far(freviews,years,filename)	
	if not(nrows):
		freviews.seek(pos)
		freviews.truncate()
		
	# Teaching
	filename = faculty_source +os.sep +FacultyName +os.sep +"Teaching" +os.sep +'teaching evaluation data.xlsx'
	pos = fteaching.tell()
	fteaching.write(headerstring)
	nrows = teaching2latex_far(fteaching,years,filename,Anonymous_Flag)	
	if not(nrows):
		fteaching.seek(pos)
		fteaching.truncate()
			
br.close()
fgrants.close()
fprops.close()
fur.close()
for i in range(len(pubfiles)):
	fpubs[i].close() 
fthesis.close() 
fpawards.close()
fsawards.close()
fservice.close()
freviews.close()

os.system('xelatex annual_report.tex')
os.system('biber annual_report.bcf')
os.system('xelatex annual_report.tex')
print("trying to delete annual_report.pdf file.  If this gets stuck, delete annual_report.pdf yourself and it should continue")
print("If it doesn't continue after that, hit ctrl-c, delete annual_report.pdf and try again")
while True:
	try:
		if os.path.exists("annual_report.pdf"):
			os.remove("annual_report.pdf")
		break
	except OSError as err:
		continue
os.system('xelatex annual_report.tex')
os.remove('annual_report.aux')
os.remove('annual_report.bbl')
os.remove('annual_report.bcf')
os.remove('annual_report.blg')
os.remove('annual_report.log')
os.remove('annual_report.out')
os.remove('annual_report.run.xml')
os.remove('annual_report.toc')
#os.remove('annual_report-blx.bib')
#os.remove("annual_report.synctex(busy)")
