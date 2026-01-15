#!/bin/zsh

# This script resets folders
# Argument 1 is the location of make_cv
# Argument 2 is the department folder
cd "$2"
for file in *; do
	rm ${file}/*/*.xlsx;
	reset.bash "$1/src/make_cv/files" $file xlsx;
	rm -rf ${file}/make_cv/FAR_docx
	cp -r "$1/src/make_cv/files/make_cv/FAR_docx" ${file}/make_cv;
	replace_line.sh "${file}/make_cv/FAR/make_cv.cfg" "${file}/make_cv/FAR_docx/make_cv.cfg" "googleid =";
	replace_line.sh "${file}/make_cv/FAR/make_cv.cfg" "${file}/make_cv/FAR_docx/make_cv.cfg" "orcid =";
	replace_line.sh "${file}/make_cv/FAR_docx/make_cv.cfg" "${file}/make_cv/Collaborators/make_cv.cfg" "gradthesesfile =";
	replace_line.sh "${file}/make_cv/FAR_docx/make_cv.cfg" "${file}/make_cv/Collaborators/make_cv.cfg" "grantsfile =";
done
