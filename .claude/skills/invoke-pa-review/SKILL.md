---
name: invoke-pa-review
description: Use when the user wants to review a prior authorization case, mentions a PA case by number or name, or says "review case"
---

Submit a prior authorization case to the AI clinical review engine.

**Step 1 — Resolve the case file:**

List `data/sample_pa_cases/*.json` and match `$ARGUMENTS` against filenames. Match on case number (1-5 from the sorted filename prefix) or any keyword in the filename (e.g., "lumbar", "keytruda", "rhinoplasty"). If no match or empty arguments, ask which case to review.

**Step 2 — Run the review:**

```
uv run python -m prior_auth_demo.command_line_demo --case data/sample_pa_cases/<matched_file>
```

**Step 3 — Summarize:**

After the CLI output, provide a brief conversational summary:
- For approvals: cite the confidence score and key guideline reference
- For denials: explain the specific clinical reason (e.g., cosmetic, diagnosis mismatch)
- For pended cases: highlight what was missing or ambiguous
