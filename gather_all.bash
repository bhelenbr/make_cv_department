#!/bin/bash

# Run this script from the "Department Data" folder

YEAR=$(date "+%Y")

# I assume this is being run in January
let YEAR=$YEAR-1

echo "Undergraduate Research"
if [ ! -d "Undergraduate Research" ]; then
	mkdir "Undergraduate Research"
	mkdir "Undergraduate Research/Historical"
fi
cd "Undergraduate Research"
if [ ! -d Historical/${YEAR} ]; then
  mkdir Historical/${YEAR}
fi
mv -n "undergraduate research data.xlsx" Historical/${YEAR}
UR_gather.py "$1"
cd ..

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
service_gather.py "$1"
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
personal_awards_gather.py "$1"
student_awards_gather.py "$1"
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
srs_gather.py "$1"
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
pubs_gather.py "$1" journal 
echo "Invited"
pubs_gather.py "$1" invited
echo "Patent"
pubs_gather.py "$1" patent
echo "Refereed"
pubs_gather.py "$1" refereed
echo "Conference"
pubs_gather.py "$1" conference
echo "Book"
pubs_gather.py "$1" book
cd ..

echo "Reviewing"
if [ ! -d Reviewing ]; then
  mkdir Reviewing
  mkdir Reviewing/Historical
fi
cd Reviewing
if [ ! -d Historical/${YEAR} ]; then
  mkdir Historical/${YEAR}
fi
mv -n "reviews data.xlsx" Historical/${YEAR}
review_gather.py "$1"
cd ..

echo "Thesis"
if [ ! -d Thesis ]; then
  mkdir Thesis
  mkdir Thesis/Historical
fi
cd Thesis
if [ ! -d Historical/${YEAR} ]; then
  mkdir Historical/${YEAR}
fi
mv -n "thesis data.xlsx" Historical/${YEAR}
mv -n "current student data.xlsx" Historical/${YEAR}
thesis_gather.py "$1"
current_grads_gather.py "$1"
cd ..