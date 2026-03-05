#!/bin/zsh

# First argument is the directory containing the University Data Files
# Second argument is the department director
employee_id_scatter.py "$1"/Faculty\ List* "$2"
advising_eval_scatter.py "$1"/CU_FAR_ADVIS_EVAL_* "$2"
advisee_counts_scatter.py -y 2025 "$1"/CU_FAR_ADVISEE_LIST_* "$2"
current_grads_scatter.py "$1"/CU_FAR_ADVISEE_LIST_* "$2"
teaching_eval_scatter.py "$1"/CU_FAR_ALL_CRSES_* "$2"
UR_scatter.py "$1"/CU_FAR_PROJ_CLASS_* "$2"
expenditures_scatter.py "$1"/CU_FAR_EXPENDITURES_* "$2"
proposals_scatter.py "$1"/CU_FAR_PROPS_* "$2"
grants_scatter.py "$1"/CU_FAR_AWARDS_* "$2"
UR_honors_scatter.py -y 2025 "$1"/FAR\ 2025* "$2"
UR_mcnair_scatter.py -y 2025 "$1"/McNair* "$2"
prospective_scatter.py "$1"/Personal\ Visit\ Information.xlsx "$2"
service_scatter.py -y 2025 "$1"/Service\ Master* "$2"
thesis_scatter.py "$1"/ETDAdmin* "$2"

