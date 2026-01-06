#!/bin/zsh

for file in [A-Z]?*; do
	echo "$file" 
	cd "$file/make_cv/FAR_docx"
	test_far.py -p "$@"
	cd ../../..
done
