---
name: invoke-pa-review-all
description: Use when the user wants to review all PA cases, run all cases, or see a summary of all determinations
---

Submit all 5 prior authorization cases to the AI clinical review engine.

Run: `python -m prior_auth_demo.command_line_demo --all`

This takes 2-3 minutes (5 Claude API calls). After the output, provide a conversational summary highlighting:
1. Which cases were approved and why
2. Which were denied and the specific reason
3. Which were pended and what was missing or ambiguous
4. The overall pattern: the system approves clear cases, denies when there's no medical necessity, and routes ambiguous/incomplete cases to human review — never auto-denying
