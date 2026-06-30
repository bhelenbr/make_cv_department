#!/bin/zsh

set -e

# Get current year
YEAR=$(date +%Y)

# First argument is the directory containing the University Data Files
# Second argument is the department director

if ls "$1"/Faculty\ List* 1> /dev/null 2>&1; then
    echo "Processing Faculty List file for employee_id_scatter.py"
    employee_id_scatter.py "$1"/Faculty\ List* "$2"
else
    echo "Warning: Faculty List file not found in $1, skipping employee_id_scatter.py"
fi

if ls "$1"/CU_FAR_ADVIS_EVAL_* 1> /dev/null 2>&1; then
    echo "Processing CU_FAR_ADVIS_EVAL file for advising_eval_scatter.py"
    advising_eval_scatter.py "$1"/CU_FAR_ADVIS_EVAL_* "$2"
else
    echo "Warning: CU_FAR_ADVIS_EVAL file not found in $1, skipping advising_eval_scatter.py"
fi

if ls "$1"/CU_FAR_ADVISEE_LIST_* 1> /dev/null 2>&1; then
    echo "Processing CU_FAR_ADVISEE_LIST file for advisee_counts_scatter.py and current_grads_scatter.py"
    advisee_counts_scatter.py "$1"/CU_FAR_ADVISEE_LIST_* "$2"
    current_grads_scatter.py "$1"/CU_FAR_ADVISEE_LIST_* "$2"
else
    echo "Warning: CU_FAR_ADVISEE_LIST file not found in $1, skipping advisee_counts_scatter.py and current_grads_scatter.py"
fi

files=("$1"/CU_FAR_ALL_CRSES_*(N))
if (( ${#files} )); then
    for file in "$files[@]"; do
        echo "Processing $file for teaching_eval_scatter.py"
        teaching_eval_scatter.py "$file" "$2"
    done
else
    echo "Warning: CU_FAR_ALL_CRSES file not found in $1, skipping teaching_eval_scatter.py"
fi

if ls "$1"/CU_FAR_PROJ_CLASS_* 1> /dev/null 2>&1; then
    echo "Processing CU_FAR_PROJ_CLASS file for UR_scatter.py"
    UR_scatter.py "$1"/CU_FAR_PROJ_CLASS_* "$2"
else
    echo "Warning: CU_FAR_PROJ_CLASS file not found in $1, skipping UR_scatter.py"
fi

files=("$1"/CU_FAR_EXPENDITURES_*(N))
if (( ${#files} )); then
    for file in "$files[@]"; do
        echo "Processing $file for expenditures_scatter.py"
        expenditures_scatter.py "$file" "$2"
    done
else
    echo "Warning: CU_FAR_EXPENDITURES file not found in $1, skipping expenditures_scatter.py"
fi

if ls "$1"/CU_FAR_PROPS_* 1> /dev/null 2>&1; then
    echo "Processing CU_FAR_PROPS file for proposals_scatter.py"
    proposals_scatter.py "$1"/CU_FAR_PROPS_* "$2"
else
    echo "Warning: CU_FAR_PROPS file not found in $1, skipping proposals_scatter.py"
fi

if ls "$1"/CU_FAR_AWARDS_* 1> /dev/null 2>&1; then
    echo "Processing CU_FAR_AWARDS file for grants_scatter.py"
    grants_scatter.py "$1"/CU_FAR_AWARDS_* "$2"
else
    echo "Warning: CU_FAR_AWARDS file not found in $1, skipping grants_scatter.py"
fi

if ls "$1"/FAR\ $YEAR* 1> /dev/null 2>&1; then
    echo "Processing FAR $YEAR file for UR_honors_scatter.py"
    UR_honors_scatter.py -y $YEAR "$1"/FAR\ $YEAR* "$2"
else
    echo "Warning: FAR $YEAR file not found in $1, skipping UR_honors_scatter.py"
fi

if ls "$1"/McNair* 1> /dev/null 2>&1; then
    echo "Processing McNair file for UR_mcnair_scatter.py"
    UR_mcnair_scatter.py -y $YEAR "$1"/McNair* "$2"
else
    echo "Warning: McNair file not found in $1, skipping UR_mcnair_scatter.py"
fi

if ls "$1"/Personal\ Visit\ Information.xlsx 1> /dev/null 2>&1; then
    echo "Processing Personal Visit Information.xlsx file for prospective_scatter.py"
    prospective_scatter.py "$1"/Personal\ Visit\ Information.xlsx "$2"
else
    echo "Warning: Personal Visit Information.xlsx file not found in $1, skipping prospective_scatter.py"
fi

if ls "$1"/Service\ Master* 1> /dev/null 2>&1; then
    echo "Processing Service Master file for service_scatter.py"
    service_scatter.py -y $YEAR "$1"/Service\ Master* "$2"
else
    echo "Warning: Service Master file not found in $1, skipping service_scatter.py"
fi

if ls "$1"/ETDAdmin* 1> /dev/null 2>&1; then
    echo "Processing ETDAdmin file for thesis_scatter.py"
    thesis_scatter.py "$1"/ETDAdmin* "$2"
else
    echo "Warning: ETDAdmin file not found in $1, skipping thesis_scatter.py"
fi

