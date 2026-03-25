# Demo Script — CLI Walkthrough

> **Format**: Microsoft Teams screen share from your desktop
> **Duration**: 5-6 minutes for CLI demo, 2 minutes for architecture context
> **Fallback**: If API issues occur, re-run the case — LLM outputs vary

---

## Prerequisites (10 minutes before)

**Bash:**

```bash
# Start Docker Desktop, then:
make setup-fhir     # HAPI FHIR + Synthea patients (~60s first time)
make dev            # FastAPI server on localhost:8000
```

**PowerShell:**

```powershell
# Start Docker Desktop, then:
docker compose up -d
python -m prior_auth_demo.mock_healthcare_services.load_fhir_data
uvicorn prior_auth_demo.healthcare_api_server:app --reload --port 8000
```

Verify: `http://localhost:8000` (dashboard), `http://localhost:8080/fhir` (HAPI FHIR).

---

## Opening (30 seconds)

Share screen showing the solution architecture diagram or slide deck.

> "I built a working demo of an AI-driven prior authorization system. It uses Claude with FHIR R4 tool use to evaluate PA requests against CMS coverage criteria — the same workflow your clinical reviewers do manually today. Let me show you."

Switch to terminal.

---

## Demo Flow (5 minutes)

### Case 1: Clear Approval — Lumbar MRI (60s)

> File: `01_lumbar_mri_clear_approval.json`

```bash
make review  # bash
```
```powershell
python -m prior_auth_demo.command_line_demo --case data/sample_pa_cases/01_lumbar_mri_clear_approval.json  # PowerShell
```

> "This is a lumbar MRI request for radiculopathy. The patient has 12 sessions of physical therapy, tried NSAIDs with only partial improvement, and has documented radiculopathy. Watch how Claude uses tools — it validates the NPI, looks up the ICD-10 codes, checks CMS coverage criteria, then produces a determination."

**Point out**: APPROVED badge, high confidence, specific guideline citations (CMS LCD L35028, ACR Appropriateness Criteria).

> "Notice it cites the exact coverage criteria it used — CMS LCD L35028 for spine MRI. An auditor can trace every decision."

### Case 2: Missing Documentation — Humira (45s)

> File: `04_humira_missing_documentation.json`

```bash
python -m prior_auth_demo.command_line_demo --case data/sample_pa_cases/04_humira_missing_documentation.json  # bash & PowerShell
```

> "Now a Humira request for rheumatoid arthritis. The provider says the patient 'failed methotrexate' but doesn't include dose, duration, or reason for discontinuation."

**Point out**: PENDED_MISSING_INFO, specific missing items listed, "Would route to human clinical reviewer" message.

> "The system doesn't deny — it tells the provider exactly what to submit. That's the CMS-0057-F compliance requirement."

### Case 3: Complex Review — Spinal Fusion (45s)

> File: `03_spinal_fusion_complex_review.json`

```bash
python -m prior_auth_demo.command_line_demo --case data/sample_pa_cases/03_spinal_fusion_complex_review.json  # bash & PowerShell
```

> "A spinal fusion with mixed signals — some criteria met, but only 8 PT sessions instead of 12, elevated A1C, no second epidural injection."

**Point out**: PENDED_FOR_REVIEW (not DENIED), identifies specific gaps.

> "Key design decision: ambiguous cases always go to a human reviewer — the system never converts a borderline case into a denial. The confidence threshold is 0.85 for auto-approval."

### Case 4: Urgent Oncology — Keytruda (45s)

> File: `05_keytruda_urgent_oncology.json`

```bash
python -m prior_auth_demo.command_line_demo --case data/sample_pa_cases/05_keytruda_urgent_oncology.json  # bash & PowerShell
```

> "Keytruda for stage IIIA lung cancer. PD-L1 at 65%, no EGFR or ALK mutations, ECOG 1. This is an NCCN Category 1 recommendation — the gold standard."

**Point out**: APPROVED with high confidence, NCCN citation, notes urgency.

> "Under CMS-0057-F, oncology cases have a 72-hour SLA. The system flags the urgency."

### Case 5: Denial — Cosmetic Rhinoplasty (45s)

> File: `02_cosmetic_rhinoplasty_denial.json`

```bash
python -m prior_auth_demo.command_line_demo --case data/sample_pa_cases/02_cosmetic_rhinoplasty_denial.json  # bash & PowerShell
```

> "A rhinoplasty coded with a skin condition diagnosis — actinic keratosis. There's no functional indication, no nasal obstruction documented."

**Point out**: DENIED, identifies cosmetic + diagnosis-procedure mismatch.

> "This is the only case the system denies — clear lack of medical necessity. The system explicitly determined this isn't covered, not because confidence was low. In production, even denials would route through human review before reaching the provider."

---

## Architecture Context (2 minutes)

> "What you just saw is the core engine — Step 1 of a progressive build. The same engine powers a REST API with Swagger docs and a web dashboard."

If time permits, briefly show:
- `http://localhost:8000` — web dashboard
- `http://localhost:8000/docs` — Swagger API

> "The architecture scales to Azure — Container Apps for compute, Azure Health Data Services for FHIR, Service Bus for async processing. The demo uses the same Anthropic SDK that's available through Azure AI Foundry."

---

## Anticipated Questions

| Question | Response |
|----------|----------|
| "Why not auto-deny?" | The system auto-approves clear cases and routes ambiguous ones to human review — it never converts a borderline case into a denial. Only explicit non-coverage (like cosmetic procedures) results in a denial, and even those route through human review in production. |
| "How accurate is it?" | The system cites specific guidelines. Accuracy depends on guideline completeness, not LLM hallucination. |
| "What about PHI?" | All demo data is synthetic (Synthea). Production uses PHI tokenization before the LLM. |
| "Why Claude?" | Tool use pattern — Claude calls structured tools (NPI, ICD-10, CMS coverage) instead of generating from memory. |
| "How does this scale?" | Azure Container Apps, Service Bus for async, PostgreSQL for audit. See solution architecture. |
