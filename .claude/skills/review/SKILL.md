---
name: review
description: Use when the user wants to review a prior authorization case, mentions a PA case by number or name, or says "review case"
---

Review a prior authorization case using the clinical review engine.

Map `$ARGUMENTS` to a case file:

| Match | File |
|-------|------|
| 1, lumbar, mri, back | `01_lumbar_mri_clear_approval.json` |
| 2, rhinoplasty, cosmetic, nasal | `02_cosmetic_rhinoplasty_denial.json` |
| 3, spinal, fusion, spine | `03_spinal_fusion_complex_review.json` |
| 4, humira, adalimumab, ra | `04_humira_missing_documentation.json` |
| 5, keytruda, oncology, lung, cancer | `05_keytruda_urgent_oncology.json` |

If no match or empty arguments, ask which case to review and list the 5 options.

Run: `python -m prior_auth_demo.command_line_demo --case data/sample_pa_cases/<matched_file>`

After output, briefly summarize: determination, confidence, and one key rationale point.
