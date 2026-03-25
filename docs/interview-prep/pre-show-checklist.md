# Pre-Show Checklist -- 1 Hour Before
## AI-Driven Prior Authorization — Autonomize AI Interview

> Work through this checklist before sending the email and before presenting.
> For study material, see [study-guide.md](study-guide.md). For speaking notes, see [speaker-script.md](../presentation/speaker-script.md).

---

## Key Statistics (Verified)

All statistics in the presentation have been verified against primary sources:
- [x] CAQH costs: $10.97 provider / $3.52 payer / $0.05 electronic (2024 CAQH Index, 2023 data)
- [x] AMA burden: 13 hours/week, 39 PAs/week, 93% care delays (2024 AMA Survey)
- [x] Altais results: 45% faster, 54% fewer errors, 50% auto-determination (BusinessWire Feb 2026)
- [x] Autonomize compliance: SOC 2 Type II + HIPAA (confirmed via trust.autonomize.ai). No HITRUST — if asked, say: "Azure services are HITRUST-certified; application-layer HITRUST assessment is a Phase 3 deliverable"

---

## Before Sending Email

- [ ] Read `email-draft.md` -- personalize tone, check formality level
- [ ] Verify demo link placeholder is updated (or remove if demo not deployed)
- [ ] Confirm attachment includes slide deck (PowerPoint or PDF)
- [ ] Confirm diagram PNGs render at readable size
- [ ] Spell-check: Paul Prae, www.paulprae.com (never misspelled)
- [ ] Check panel names spelled correctly: Kris Nair, Suresh Gopalakrishnan, Ujjwal Rajbhandari
- [ ] Verify email tone and content match your voice

---

## Before Presenting -- Content Accuracy

- [ ] Verify Altais metrics: 45% review time reduction, 54% error reduction, 50% auto-approval
- [ ] Verify CAQH numbers: $10.97 provider, $3.52 payer, ~$0.05 automated (2024 Index)
- [ ] Verify CMS-0057-F: Phase 1 live Jan 2026, Phase 2 Jan 2027
- [ ] Verify Autonomize: Pegasus Program (Nov 2025), Azure Marketplace, ServiceNow partnership (Mar 2026)
- [ ] Spot-check 5 source URLs from appendix -- all should load

---

## Before Presenting -- Azure Service Names

- [ ] Azure AI Foundry (not "Azure OpenAI Service" -- rebranded)
- [ ] Azure AI Document Intelligence (not "Form Recognizer" -- rebranded)
- [ ] Microsoft Entra ID (not "Azure AD" -- rebranded)
- [ ] Azure Health Data Services (not "Azure API for FHIR" -- evolved)
- [ ] Azure Container Apps (confirm still GA, not deprecated)

---

## Before Presenting -- Rehearsal

- [ ] **Architecture overview**: Practice 2-minute walkthrough of [`docs/architecture/solution-architecture.md`](../architecture/solution-architecture.md)
- [ ] Read [speaker-script.md](../presentation/speaker-script.md) opening thesis aloud
- [ ] Read closing summary aloud
- [ ] Time yourself on slides 1-6 (target: 15 min)
- [ ] Review "don't elaborate" topics in speaker-script.md

---

## Before Presenting -- Diagrams

- [ ] All 6 diagrams render in PowerPoint at readable size
- [ ] Diagram labels match component names in speaker notes
- [ ] No diagram has more text than fits comfortably on a slide

---

## Before Presenting -- Demo

### Infrastructure (10 minutes before)
- [ ] Docker Desktop running (open it; takes ~30s to start)
- [ ] Start HAPI FHIR + load data:
  - Bash: `make setup-fhir`
  - PowerShell: `docker compose up -d` then `python -m prior_auth_demo.mock_healthcare_services.load_fhir_data`
- [ ] Verify FHIR is responding: open `http://localhost:8080/fhir/metadata` in browser
- [ ] Start FastAPI server:
  - Bash: `make dev`
  - PowerShell: `uvicorn prior_auth_demo.healthcare_api_server:app --reload --port 8000`
- [ ] `.env` has valid `ANTHROPIC_API_KEY` and `FHIR_SERVER_URL=http://localhost:8080/fhir`

### Smoke Test (5 minutes before)
- [ ] Single case produces APPROVED determination:
  - Bash: `make review`
  - PowerShell: `python -m prior_auth_demo.command_line_demo --case data/sample_pa_cases/01_lumbar_mri_clear_approval.json`
- [ ] All 5 cases produce expected outcomes (approve, deny, pend, complex, urgent):
  - Bash: `make review-all`
  - PowerShell: `python -m prior_auth_demo.command_line_demo --all`
- [ ] Open `http://localhost:8000` — dashboard loads, case dropdown populated
- [ ] Open `http://localhost:8000/docs` — Swagger UI renders all endpoints
- [ ] Open `http://localhost:8080` — HAPI FHIR welcome page shows
- [ ] Check response times — should be under 30 seconds per case
- [ ] Verify confidence scores are in reasonable range (0.0-1.0)
- [ ] Verify reasoning includes evidence citations
- [ ] **Fallback plan**: If dashboard fails → demo via Swagger UI (`/docs`); if that fails → CLI (bash: `make review` / PowerShell: `python -m prior_auth_demo.command_line_demo --case data/sample_pa_cases/01_lumbar_mri_clear_approval.json`); if all fail → walk through architecture diagrams
- [ ] **Backup recording**: Screenshot or recording of a successful demo run in case of API outage

---

## Before Presenting -- Teams Screen Share

- [ ] **This desktop is the demo machine** — no separate laptop needed
- [ ] **Test screen share resolution**: Start a Teams test call → Share screen → confirm text is crisp and readable
- [ ] **Close distracting apps**: Slack, email, personal browser tabs, notifications (Focus Assist ON)
- [ ] **Pre-load browser**: Open `http://localhost:8000` and `http://localhost:8000/docs` in separate tabs before the call
- [ ] **Services running**: Docker Desktop started, FHIR loaded (see Infrastructure above), FastAPI server running, internet connected

---

## Risk Awareness

### Content Accuracy Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Altais metrics (45%/54%/50%) challenged by panel | Low | Medium | Source verified: BusinessWire Feb 2026. Have URL ready. |
| CAQH cost numbers questioned | Low | Low | Source verified: 2024 CAQH Index PDF. Payer cost is $3.52 per transaction. |
| CMS-0057-F timeline questioned | Low | Medium | Phase 1 live Jan 2026, Phase 2 Jan 2027. CMS fact sheet URL ready. |
| Autonomize platform claims challenged | Medium | High | Only cite publicly verified facts (Pegasus Program, Azure Marketplace, ServiceNow partnership, SOC 2, 3 of top 5 plans). No internal platform claims. |
| Claude healthcare connectors availability via API unclear | Medium | Low | Frame as "Claude platform capability" -- demo uses Anthropic SDK tool-use pattern regardless. |

### Presentation Readiness Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Paul goes over time (known tendency) | High | Medium | Priority-tiered slides. 3-minute rule per slide. Coaching doc has time awareness tips. |
| Paul tells stories instead of answering directly | High | Medium | "Don't elaborate" flags on each slide. Pivot phrases in speaker-script.md. |
| Panel asks about FHIR Da Vinci / SMART on FHIR details | Medium | Medium | Redirect: "That's a discovery-phase activity with the implementation team." Don't fabricate depth. |
| Panel asks about EDI X12 parsing | Low | Low | Redirect: "Integration-build detail for discovery phase." Not in Paul's depth. |
| Panel asks about traditional ML metrics (KS, PSI) | Medium | Medium | Bridge: "Those apply if we add a triage classifier. The LLM monitoring is eval-driven, not distribution-driven." |

### Demo Readiness Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Anthropic PA review skill doesn't install or work | Medium | High | Test BEFORE the interview. Have mock data fallback. |
| Azure deployment fails | Medium | Low | Local demo is perfectly acceptable. Don't force Azure. |
| Demo doesn't match slide architecture | Low | High | Demo prompt explicitly aligned to slide narrative. Demo walkthrough script in presentation.md. |
| Panel wants to try unusual PA cases | Medium | Low | Have 3-5 mock cases covering different outcomes. Acknowledge demo uses mock data. |

### Knowledge Gap Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Suresh probes payer-specific LOB terminology | Medium | Medium | Be honest: "My payer experience is at the integration level -- I'd want to work with your clinical operations team on LOB-specific rules." |
| Ujjwal asks about TOGAF or enterprise architecture frameworks | Low | Low | Paul doesn't claim TOGAF. Redirect to practical experience: "I focus on iterative architecture -- design, validate, iterate." |
| Panel asks about Snowflake/dbt details | Low | Low | Paul has ~6 months. Mention Arine experience briefly, don't deep-dive. |
| Questions about Autonomize platform internals | High | Medium | "No public API documentation available. These are discovery questions I'd explore during onboarding." |

---

## Items Paul MUST Verify Before Presenting

1. **Read all speaker notes aloud** -- every slide. Time yourself. Flag anything that sounds unnatural.
2. **Check diagram rendering** at presentation display size -- text readability at projector resolution.
3. **Test the demo** -- PA review skill installs, mock data produces reasonable output.
4. **Review Azure-to-AWS mapping** in [study-guide.md](study-guide.md) -- be ready for Ujjwal's questions.
5. **Review assumptions and discovery questions** in [study-guide.md](study-guide.md) -- these show depth and honesty.
6. **Verify all cited URLs work** -- spot-check 5 random source links from the appendix.
7. **Practice the 60-second opening thesis** from [speaker-script.md](../presentation/speaker-script.md).
8. **Practice the 30-second closing summary** -- this is your landing point no matter what.

---

## Sign-Off

| Reviewer | Date | Status | Notes |
|----------|------|--------|-------|
| Paul Prae | | | |
