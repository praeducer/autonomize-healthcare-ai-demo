# UAT Guide — Prior Authorization Demo

> **SSOT for**: How to manually test each user story — what to check and what "good" looks like.
>
> **Purpose**: Walk through every user-facing feature and verify it works as a human would experience it. Automated tests cover correctness — this guide covers *experience*.
>
> **When to run**: After each build step, and before any demo or interview.

**Related documents:**

- Story definitions (IDs, roles, acceptance criteria): [`docs/user-stories.md`](user-stories.md)
- Interface setup and usage commands: [`docs/user-guide.md`](user-guide.md)
- Pre-interview checklist: [`docs/plans/human-tasks.md`](plans/human-tasks.md)

LLM outputs are non-deterministic. If a case gives an unexpected result, re-run once. Consistent wrong results = bug.

---

## US-1: Submit a case and receive a determination

**Goal**: Any interface accepts a PA case and returns a clinical determination within 60 seconds.

| Interface | How to test | What to look for |
|-----------|------------|-----------------|
| CLI | Run single case per [User Guide — CLI](user-guide.md#2-cli-terminal) | APPROVED badge, confidence %, rationale, citations, processing time |
| Claude Code | `/invoke-pa-review` | Same output, conversational context |
| API (Step 2+) | POST `/api/v1/prior-auth/review` via Swagger | JSON response with determination, confidence, rationale |
| Dashboard (Step 3+) | Select case → Submit | Loading spinner → result card with badge, confidence bar, rationale |

---

## US-2: Evidence-backed reasoning with citations

**Goal**: Every determination includes clinical rationale (2+ sentences) and guideline citations.

Run all cases per [User Guide — CLI](user-guide.md#2-cli-terminal) or `/invoke-pa-review-all` (Claude Code) and read each result:

| Case | Check rationale for... |
|------|----------------------|
| 1 — Lumbar MRI | Mentions "conservative treatment failure" or "radiculopathy" |
| 2 — Rhinoplasty | Mentions "cosmetic" and "diagnosis mismatch" |
| 3 — Spinal Fusion | Identifies specific gaps (PT sessions, ESI, A1C, BMI) |
| 4 — Humira | Lists missing items (methotrexate dose, labs, DAS28) |
| 5 — Keytruda | Mentions NCCN, PD-L1, or oncology urgency |

**What you're judging**: Does the rationale read like a clinical reviewer wrote it? Would you trust this explanation? Would an ex-Elevance (or similar payer) reviewer find the ICD-10 codes, scenarios, and tone realistic?

---

## US-3: Ambiguous cases route to human review

**Goal**: Cases with mixed evidence are PENDED, never auto-denied.

| Case | Expected determination | Why |
|------|----------------------|-----|
| 3 — Spinal Fusion | PENDED_FOR_REVIEW | Some criteria met, some gaps — ambiguous |
| 4 — Humira | PENDED_MISSING_INFO | Clinical picture plausible but docs missing |

If either returns DENIED, that's a bug — the system should never auto-deny ambiguous cases.

---

## US-4: Denials include specific clinical reasons

**Goal**: Case 2 (Rhinoplasty) returns DENIED with a clear explanation.

Check that the rationale specifically explains *why* — cosmetic indication, diagnosis-procedure mismatch, no functional impairment documented.

---

## US-5: Missing-info cases list exactly what's needed

**Goal**: Case 4 (Humira) lists specific missing documents.

Check the `missing_documentation` field contains actionable items a provider could respond to (e.g., "methotrexate dose and duration", "DAS28 score", "TB screening results"). Vague responses like "more documentation needed" = bug.

---

## US-6: REST API with Swagger docs (Step 2+)

Open `http://localhost:8000/docs` — Swagger UI should render with all endpoints. Try submitting a case directly from the Swagger interface.

---

## US-7: Immutable audit trail (Step 2+)

After submitting cases via any interface, verify they appear in `GET /api/v1/prior-auth/determinations`. Check the SQLite database directly:

- **Bash**: `sqlite3 data/audit_trail.db "SELECT determination, confidence_score FROM determinations;"`
- **PowerShell**: `uv run python -c "import sqlite3; conn = sqlite3.connect('data/audit_trail.db'); print(conn.execute('SELECT determination, confidence_score FROM determinations').fetchall())"`

Records should accumulate, never disappear.

---

## US-8: Web dashboard (Step 3+)

Open `http://localhost:8000`. Submit all 5 cases in demo order: **1 → 4 → 3 → 5 → 2** (clear approval → missing docs → ambiguous → urgent → denial). This order tells a clinical story.

**Timing**: Target 5-6 minutes total for all 5 cases, each case under 60 seconds. After all 5 cases, verify the history table shows all 5 with correct determinations.

---

## US-9: Screen share readability (Step 3+)

Share your screen via Teams. All text readable? Badges visible? No horizontal scrolling? This is your interview surface. Have someone else watch — are badges and rationale clear to a non-technical viewer?

---

## Regression: All interfaces work simultaneously

After each new step, verify previous interfaces still work:

| Check | How |
|-------|-----|
| CLI works standalone | Run single case per [User Guide — CLI](user-guide.md#2-cli-terminal) |
| CLI works without Docker | Stop Docker (`docker compose down`), then run CLI — should still work |
| Swagger still renders (Step 2+) | Open `http://localhost:8000/docs` |
| API returns JSON, not HTML (Step 3+) | `GET /api/v1/prior-auth/sample-cases` — should return JSON, not dashboard HTML |

---

## Quick Reference

| Story | What to test | Automated? |
|-------|-------------|-----------|
| US-1 | Determination returned | Timing and structure: yes. Clinical quality: **no — UAT only** |
| US-2 | Rationale quality | Keywords: yes. Reads like a clinician: **no — UAT only** |
| US-3 | Ambiguous → pended | Determination value: yes. Reasoning appropriateness: **no — UAT only** |
| US-4 | Denial reasons | Keywords: yes. Specificity and clarity: **no — UAT only** |
| US-5 | Missing docs listed | Non-empty list: yes. Actionable items: **no — UAT only** |
| US-6 | Swagger works | HTTP 200: yes. Usable UI: **no — UAT only** |
| US-7 | Audit trail | Records exist: yes. Data integrity over time: **no — UAT only** |
| US-8 | Dashboard UX | Renders: yes. Professional appearance: **no — UAT only** |
| US-9 | Screen share readability | N/A: **UAT only** |
