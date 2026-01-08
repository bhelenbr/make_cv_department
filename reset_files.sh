#!/bin/zsh

# This script resets folder
cd "$2"
for file in *; do
	rm ${file}/*/*.xlsx;
	reset.bash "$1/src/make_cv/files" $file xlsx;
	rm -rf ${file}/make_cv/FAR_docx
	cp -r "$1/src/make_cv/files/make_cv/FAR_docx" ${file}/make_cv;
	replace_line.sh ${file}/make_cv/FAR/make_cv.cfg ${file}/make_cv/FAR_docx/make_cv.cfg "googleid =";
	replace_line.sh ${file}/make_cv/FAR/make_cv.cfg ${file}/make_cv/FAR_docx/make_cv.cfg "orcid =";
done
	 