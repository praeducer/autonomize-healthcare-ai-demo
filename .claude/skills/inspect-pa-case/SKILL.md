---
name: inspect-pa-case
description: Use when the user wants to see a PA case's clinical data before running AI review, or asks what's in a case
---

Inspect a prior authorization case's clinical data without running AI review. No API calls — purely local FHIR Bundle parsing.

**Step 1 — Resolve the case file:**

List `data/sample_pa_cases/*.json` and match `$ARGUMENTS` against filenames. Match on case number (1-5 from the sorted filename prefix) or any keyword in the filename (e.g., "lumbar", "keytruda"). If no match or empty arguments, ask which case to inspect.

**Step 2 — Show the clinical data:**

```
uv run python -m prior_auth_demo.command_line_demo --inspect data/sample_pa_cases/<matched_file>
```

**Step 3 — Explain what the reviewer will see:**

After the output, briefly explain what this data means for the AI review — e.g., "This case has documented conservative treatment failure and a valid NPI. When Claude reviews it, it will check these ICD-10 codes against CMS coverage criteria for CPT 72148."

Suggest: Use `/invoke-pa-review <same case>` to run the AI review on this case.
