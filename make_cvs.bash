#!/bin/zsh

for file in [A-Z]?*; do
	echo "$file" 
	cd "$file/make_cv/CV"
	make_far "$@"
	cd ../../..
done
