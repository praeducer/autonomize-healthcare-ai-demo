# Technical Decisions — Review Before Demo Build

> Paul: review these before starting the demo implementation. Items are ranked by impact on the presentation.

## D-001: HITRUST certification claim is unverified (MEDIUM impact)

- **Decision:** The solution architecture references HITRUST compliance. Autonomize AI's HITRUST CSF certification status could not be independently verified from public sources.
- **Why it matters:** If asked about HITRUST, redirect: "HITRUST inheritance is a compliance assessment activity — scoped as a Phase 3 deliverable." Do not assert Autonomize has HITRUST certification unless you can confirm it.
- **Action needed:** Check Autonomize's compliance page or ask directly before presenting

## D-002: CAQH payer cost verified at $3.52 (LOW impact)

- **Decision:** Use $3.52 (2024 CAQH Index, "Prior Authorization" row, "Health Plan" column) as the authoritative payer per-transaction cost
- **Why it matters:** This number appears in the presentation (Slide 2) and the demo walkthrough. If challenged, cite the 2024 CAQH Index report directly.
- **Action needed:** None — verified against published source

## D-003: AMA physician time burden corrected to 12-13 hours/week (LOW impact)

- **Decision:** Use "12-13 hours/week" (2024 AMA survey) instead of commonly cited "14 hours/week"
- **Why it matters:** More defensible if challenged. The 2024 AMA Prior Authorization Survey is the most recent data.
- **Action needed:** Verify you're comfortable saying "12 to 13 hours" in the presentation
