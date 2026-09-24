#!/bin/zsh

# Arguments are
# 1: folder containing department subfolders
# 2: make_cv folder
# 3: university data folder

if [ "$#" -lt 3 ]; then
	echo "Usage: $0 <departments-root> <make_cv folder> <university data folder>" >&2
	exit 2
fi

set -euo pipefail

# Remember where the script was invoked from so relative paths for
# arguments 2 and 3 are resolved from the caller's working directory.
INVOCATION_DIR="$PWD"

# Resolve make_cv and university data folders relative to invocation dir
MAKE_CV_DIR="$2"
if [[ "$MAKE_CV_DIR" != /* ]]; then
	MAKE_CV_DIR="${INVOCATION_DIR%/}/$MAKE_CV_DIR"
fi

UNIV_DATA_DIR="$3"
if [[ "$UNIV_DATA_DIR" != /* ]]; then
	UNIV_DATA_DIR="${INVOCATION_DIR%/}/$UNIV_DATA_DIR"
fi

cd "$1" || { echo "Cannot cd to $1" >&2; exit 2; }

for department in *; do
	[[ -d "$department" ]] || continue
	reset_files.sh "$MAKE_CV_DIR" "${department}"
	# Don't archive here: scatter_all.bash would move the university data files
	# away after the first department and the rest would find nothing.
	scatter_all.bash --no-archive "$UNIV_DATA_DIR" "${department}"
	cd "${department}"
	# First argument is the option string passed to test_far.py / test_nsfcoa.py
	# (e.g. "-q -o 4 -g 4"); remaining arguments are the faculty folders.
	make_fars_docx.bash "" *
	make_nsfcoas.bash "" *
	cd ..
done

# Archive the university Excel files once, after every department is done
archive_dir="$UNIV_DATA_DIR/$(date +%y_%m_%d)"
mkdir -p "$archive_dir"
find "$UNIV_DATA_DIR" -maxdepth 1 -type f \( -iname '*.xlsx' -o -iname '*.xls' -o -iname '*.xlsm' \) -exec mv {} "$archive_dir"/ \;
echo "Moved Excel files to $archive_dir"
