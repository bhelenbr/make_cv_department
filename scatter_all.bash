#!/bin/zsh

# First argument is the directory containing the University Data Files
# Second argument is the department director
employee_id_scatter.py "$1"/Faculty\ List* "$2"
advisee_counts_scatter.py "$1"/CU_ACAD_DEPT_ADVISOR_CT_ALLDEP_* "$2"
for file in "$1"/CU_ADVIS_EVAL_DATA_ALL*; do
	advising_eval_scatter.py "$file" "$2"; done
srs_proposals_scatter.py "$1"/CU_GM_ALL_PROPS_ALL_* "$2"
srs_grants_scatter.py "$1"/CU_INTERFOLIO_AWARDS_* "$2"
current_grads_scatter.py "$1"/CU_ACAD_STDNT_ADVISOR_LISTING* "$2"
teaching_eval_scatter.py "$1"/CU_CRSE_EVAL_DATA_ALL_* "$2"
for file in "$1"/CU_BH_PROJ_RES_CLASS_FULL*; do
	UR_scatter.py "$file" "$2"; done
UR_honors_scatter.py -y 2025 "$1"/FAR\ 2025* "$2"
UR_mcnair_scatter.py -y 2025 "$1"/McNair* "$2"
prospective_scatter.py "$1"/Personal\ Visit\ Information.xlsx "$2"
expenditures_scatter.py "$1"/CU_INTERFOLIO_ADDITIONAL_DATA_* "$2"
service_scatter.py -y 2025 "$1"/Service\ Master* "$2"

