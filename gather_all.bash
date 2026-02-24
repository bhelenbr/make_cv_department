#!/bin/bash

# Run this script from the "Department Data" folder
YEAR=$(date "+%Y")

# I assume this is being run in January
let YEAR=$YEAR-1

# Normalize first argument to an absolute path so relative/local paths
# still work after this script changes directories.
ARG=""
if [ -n "$1" ]; then
  if command -v realpath >/dev/null 2>&1; then
    ARG=$(realpath "$1")
  else
    ARG=$(python3 -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "$1")
  fi
fi
echo "Service"
if [ ! -d "Service" ]; then
	mkdir "Service"
	mkdir "Service/Historical"
fi
cd Service
if [ ! -d Historical/${YEAR} ]; then
  mkdir Historical/${YEAR}
fi
mv -n "service data.xlsx" Historical/${YEAR}
mv -n "advisee counts.xlsx" Historical/${YEAR}
mv -n "advising evaluation data.xlsx" Historical/${YEAR}
mv -n "prospective visit data.xlsx" Historical/${YEAR}
mv -n "undergraduate research data.xlsx" Historical/${YEAR}
mv -n "reviews data.xlsx" Historical/${YEAR}
service_gather.py "$ARG"
advisee_counts_gather.py "$ARG"
advising_eval_gather.py "$ARG"
prospective_gather.py "$ARG"
UR_gather.py "$ARG"
review_gather.py "$ARG"
cd ..

echo "Awards"
if [ ! -d "Awards" ]; then
	mkdir "Awards"
	mkdir "Awards/Historical"
fi
cd Awards
if [ ! -d Historical/${YEAR} ]; then
  mkdir Historical/${YEAR}
fi
mv -n "personal awards data.xlsx" Historical/${YEAR}
mv -n "student awards data.xlsx" Historical/${YEAR}
personal_awards_gather.py "$ARG"
student_awards_gather.py "$ARG"
cd ..

echo "Proposals & Grants"
if [ ! -d "Proposals & Grants" ]; then
	mkdir "Proposals & Grants"
	mkdir "Proposals & Grants/Historical"
fi
cd "Proposals & Grants"
if [ ! -d Historical/${YEAR} ]; then
  mkdir Historical/${YEAR}
fi
mv -n "proposals & grants.xlsx" Historical/${YEAR}
mv -n "expenditures.xlsx" Historical/${YEAR}
mv -n "grants.xlsx" Historical/${YEAR}
proposals_gather.py "$ARG"
expenditures_gather.py "$ARG"
grants_gather.py "$ARG"
cd ..

echo "Scholarship"
if [ ! -d Scholarship ]; then
  mkdir Scholarship
  mkdir Scholarship/Historical
fi
cd Scholarship
if [ ! -d Historical/${YEAR} ]; then
  mkdir Historical/${YEAR}
fi
mv -n *.xlsx Historical/${YEAR}
echo "Journal"
pubs_gather.py "$ARG" journal 
echo "Invited"
pubs_gather.py "$ARG" invited
echo "Patent"
pubs_gather.py "$ARG" patent
echo "Refereed"
pubs_gather.py "$ARG" refereed
echo "Conference"
pubs_gather.py "$ARG" conference
echo "Book"
pubs_gather.py "$ARG" book
mv -n "thesis data.xlsx" Historical/${YEAR}
mv -n "current student data.xlsx" Historical/${YEAR}
thesis_gather.py "$ARG"
current_grads_gather.py "$ARG"
cd ..

echo "Teaching"
if [ ! -d Teaching ]; then
  mkdir Teaching
  mkdir Teaching/Historical
fi
cd Teaching
if [ ! -d Historical/${YEAR} ]; then
  mkdir Historical/${YEAR}
fi
mv -n "teaching evaluation data.xlsx" Historical/${YEAR}
teaching_eval_gather.py "$ARG"
cd ..