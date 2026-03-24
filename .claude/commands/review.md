Review a prior authorization case using the clinical review engine.

If the user specifies a case number (1-5) or case name, run the matching case:
- Case 1 / lumbar / mri: `python -m prior_auth_demo.command_line_demo --case data/sample_pa_cases/01_lumbar_mri_clear_approval.json`
- Case 2 / rhinoplasty / cosmetic: `python -m prior_auth_demo.command_line_demo --case data/sample_pa_cases/02_cosmetic_rhinoplasty_denial.json`
- Case 3 / spinal / fusion: `python -m prior_auth_demo.command_line_demo --case data/sample_pa_cases/03_spinal_fusion_complex_review.json`
- Case 4 / humira / adalimumab: `python -m prior_auth_demo.command_line_demo --case data/sample_pa_cases/04_humira_missing_documentation.json`
- Case 5 / keytruda / oncology / lung: `python -m prior_auth_demo.command_line_demo --case data/sample_pa_cases/05_keytruda_urgent_oncology.json`

If no case is specified, use `$ARGUMENTS` to determine which case. If `$ARGUMENTS` is empty, ask the user which case to review.

Run the command and show the output. After the result, briefly summarize the determination, confidence, and key rationale points.
