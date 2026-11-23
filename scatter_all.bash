#!/bin/zsh

set -e

# Get current year
YEAR=$(date +%Y)

# First argument is the directory containing the University Data Files
# Second argument is the department director

DATA_DIR=""
DEPARTMENT_DIRECTOR=""
ARCHIVE_ENABLED=1

while [[ $# -gt 0 ]]; do
    case "$1" in
        --no-archive|-n)
            ARCHIVE_ENABLED=0
            shift
            ;;
        --help|-h)
            echo "Usage: $0 <data_dir> <department_director> [--no-archive]"
            exit 0
            ;;
        -*)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
        *)
            if [[ -z "$DATA_DIR" ]]; then
                DATA_DIR="$1"
            elif [[ -z "$DEPARTMENT_DIRECTOR" ]]; then
                DEPARTMENT_DIRECTOR="$1"
            else
                echo "Unexpected argument: $1" >&2
                exit 1
            fi
            shift
            ;;
    esac
done

if [[ -z "$DATA_DIR" || -z "$DEPARTMENT_DIRECTOR" ]]; then
    echo "Usage: $0 <data_dir> <department_director> [--no-archive]" >&2
    exit 1
fi

# if ls "$DATA_DIR"/CU_BH_MONTHLY_FACULTY_DATA* 1> /dev/null 2>&1; then
#     echo "Processing Faculty HR file using sync_faculty_folders.py"
#     sync_faculty_folders.py "$DATA_DIR"/CU_BH_MONTHLY_FACULTY_DATA* "$DEPARTMENT_DIRECTOR"
# else
#     echo "Warning: Faculty List file not found in $DATA_DIR, skipping employee_id_scatter.py"
# fi

# if ls "$DATA_DIR"/Faculty\ List* 1> /dev/null 2>&1; then
#     echo "Processing Faculty List file for employee_id_scatter.py"
#     employee_id_scatter.py "$DATA_DIR"/Faculty\ List* "$DEPARTMENT_DIRECTOR"
# else
#     echo "Warning: Faculty List file not found in $DATA_DIR, skipping employee_id_scatter.py"
# fi

if ls "$DATA_DIR"/CU_FAR_ADVIS_EVAL_* 1> /dev/null 2>&1; then
    echo "Processing CU_FAR_ADVIS_EVAL file for advising_eval_scatter.py"
    advising_eval_scatter.py "$DATA_DIR"/CU_FAR_ADVIS_EVAL_* "$DEPARTMENT_DIRECTOR"
else
    echo "Warning: CU_FAR_ADVIS_EVAL file not found in $DATA_DIR, skipping advising_eval_scatter.py"
fi

if ls "$DATA_DIR"/CU_FAR_ADVISEE_LIST_* 1> /dev/null 2>&1; then
    echo "Processing CU_FAR_ADVISEE_LIST file for advisee_counts_scatter.py and current_grads_scatter.py"
    advisee_counts_scatter.py "$DATA_DIR"/CU_FAR_ADVISEE_LIST_* "$DEPARTMENT_DIRECTOR"
    current_grads_scatter.py "$DATA_DIR"/CU_FAR_ADVISEE_LIST_* "$DEPARTMENT_DIRECTOR"
else
    echo "Warning: CU_FAR_ADVISEE_LIST file not found in $DATA_DIR, skipping advisee_counts_scatter.py and current_grads_scatter.py"
fi

files=("$DATA_DIR"/CU_FAR_ALL_CRSES_*(N))
if (( ${#files} )); then
    for file in "$files[@]"; do
        echo "Processing $file for teaching_eval_scatter.py"
        teaching_eval_scatter.py "$file" "$DEPARTMENT_DIRECTOR"
    done
else
    echo "Warning: CU_FAR_ALL_CRSES file not found in $DATA_DIR, skipping teaching_eval_scatter.py"
fi

if ls "$DATA_DIR"/CU_FAR_PROJ_CLASS_* 1> /dev/null 2>&1; then
    echo "Processing CU_FAR_PROJ_CLASS file for UR_scatter.py"
    UR_scatter.py "$DATA_DIR"/CU_FAR_PROJ_CLASS_* "$DEPARTMENT_DIRECTOR"
else
    echo "Warning: CU_FAR_PROJ_CLASS file not found in $DATA_DIR, skipping UR_scatter.py"
fi

files=("$DATA_DIR"/CU_FAR_EXPENDITURES_*(N))
if (( ${#files} )); then
    for file in "$files[@]"; do
        echo "Processing $file for expenditures_scatter.py"
        expenditures_scatter.py "$file" "$DEPARTMENT_DIRECTOR"
    done
else
    echo "Warning: CU_FAR_EXPENDITURES file not found in $DATA_DIR, skipping expenditures_scatter.py"
fi

if ls "$DATA_DIR"/CU_FAR_PROPS*.xlsx 1> /dev/null 2>&1; then
    echo "Processing CU_FAR_PROPS file for proposals_scatter.py"
    proposals_scatter.py "$DATA_DIR"/CU_FAR_PROPS*.xlsx "$DEPARTMENT_DIRECTOR"
else
    echo "Warning: CU_FAR_PROPS file not found in $DATA_DIR, skipping proposals_scatter.py"
fi

if ls "$DATA_DIR"/CU_FAR_AWARDS*.xlsx 1> /dev/null 2>&1; then
    echo "Processing CU_FAR_AWARDS file for grants_scatter.py"
    grants_scatter.py "$DATA_DIR"/CU_FAR_AWARDS*.xlsx "$DEPARTMENT_DIRECTOR"
else
    echo "Warning: CU_FAR_AWARDS file not found in $DATA_DIR, skipping grants_scatter.py"
fi

if ls "$DATA_DIR"/FAR\ $YEAR* 1> /dev/null 2>&1; then
    echo "Processing FAR $YEAR file for UR_honors_scatter.py"
    UR_honors_scatter.py -y $YEAR "$DATA_DIR"/FAR\ $YEAR* "$DEPARTMENT_DIRECTOR"
else
    echo "Warning: FAR $YEAR file not found in $DATA_DIR, skipping UR_honors_scatter.py"
fi

if ls "$DATA_DIR"/McNair* 1> /dev/null 2>&1; then
    echo "Processing McNair file for UR_mcnair_scatter.py"
    UR_mcnair_scatter.py -y $YEAR "$DATA_DIR"/McNair* "$DEPARTMENT_DIRECTOR"
else
    echo "Warning: McNair file not found in $DATA_DIR, skipping UR_mcnair_scatter.py"
fi

if ls "$DATA_DIR"/Personal\ Visit\ Information*.xlsx 1> /dev/null 2>&1; then
    echo "Processing Personal Visit Information.xlsx file for prospective_scatter.py"
    prospective_scatter.py "$DATA_DIR"/Personal\ Visit\ Information*.xlsx "$DEPARTMENT_DIRECTOR"
else
    echo "Warning: Personal Visit Information.xlsx file not found in $DATA_DIR, skipping prospective_scatter.py"
fi

if ls "$DATA_DIR"/Service\ Master* 1> /dev/null 2>&1; then
    echo "Processing Service Master file for service_scatter.py"
    service_scatter.py -y $YEAR "$DATA_DIR"/Service\ Master* "$DEPARTMENT_DIRECTOR"
else
    echo "Warning: Service Master file not found in $DATA_DIR, skipping service_scatter.py"
fi

if ls "$DATA_DIR"/ETDAdmin*.xlsx 1> /dev/null 2>&1; then
    echo "Processing ETDAdmin file for thesis_scatter.py"
    thesis_scatter.py "$DATA_DIR"/ETDAdmin* "$DEPARTMENT_DIRECTOR"
else
    echo "Warning: ETDAdmin file not found in $DATA_DIR, skipping thesis_scatter.py"
fi

if (( ARCHIVE_ENABLED )); then
    # Archive Excel files into a dated folder
    archive_dir="$DATA_DIR/$(date +%y_%m_%d)"
    mkdir -p "$archive_dir"
    find "$DATA_DIR" -maxdepth 1 -type f \( -iname '*.xlsx' -o -iname '*.xls' -o -iname '*.xlsm' \) -exec mv {} "$archive_dir"/ \;

    echo "Moved Excel files to $archive_dir"
else
    echo "Archiving disabled; leaving Excel files in place."
fi


