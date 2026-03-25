---
name: invoke-pa-review
description: Use when the user wants to review a prior authorization case, mentions a PA case by number or name, or says "review case"
---

Submit a prior authorization case to the AI clinical review engine.

Map `$ARGUMENTS` to a case file:

| Match | File | Scenario |
|-------|------|----------|
| 1, lumbar, mri, back | `01_lumbar_mri_clear_approval.json` | Clear approval — conservative treatment failure |
| 2, rhinoplasty, cosmetic, nasal | `02_cosmetic_rhinoplasty_denial.json` | Denial — cosmetic, diagnosis mismatch |
| 3, spinal, fusion, spine | `03_spinal_fusion_complex_review.json` | Complex — ambiguous criteria, routes to review |
| 4, humira, adalimumab, ra | `04_humira_missing_documentation.json` | Missing info — incomplete step therapy docs |
| 5, keytruda, oncology, lung, cancer | `05_keytruda_urgent_oncology.json` | Urgent approval — NCCN Category 1 oncology |

If no match or empty arguments, ask which case to review.

Run: `python -m prior_auth_demo.command_line_demo --case data/sample_pa_cases/<matched_file>`

After the output, provide a brief conversational summary like:
- "Case 1 was **APPROVED** at 97% confidence. Claude cited CMS LCD L35028 — the patient's 12 PT sessions and positive straight leg raise met the auto-approval criteria."
- For pended cases, highlight what was missing or ambiguous.
- For denials, explain the specific clinical reason.

This helps the user understand the clinical reasoning without re-reading the full output.
