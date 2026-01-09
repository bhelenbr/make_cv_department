#!/bin/zsh

# Arguments are 
# <folder containing department subfolders>
# <make_cv folder>
# <university data folder>

cd "$1"

for department in *; do
	reset_files.sh "$2" "${department}"
	scatter_all.bash "$3" "${department}"
	cd "${department}"
	make_fars_docx.bash -q -o 4 -g 4
	make_nsfcoas.bash
	cd ..
done
