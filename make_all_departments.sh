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
	reset_files.sh "$MAKE_CV_DIR" "${department}"
	scatter_all.bash "$UNIV_DATA_DIR" "${department}"
	cd "${department}"
	#make_fars_docx.bash -q -o 4 -g 4
	make_fars_docx.bash
	make_nsfcoas.bash
	cd ..
done
