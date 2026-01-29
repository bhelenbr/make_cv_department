#!/bin/zsh

for file in [A-Z]?*; do
	echo "$file" 
	cd "$file/make_cv/Collaborators"
	test_nsfcoa.py "$@"
	cd ../../..
done
