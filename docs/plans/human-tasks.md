# Human Tasks — Pre-Interview Checklist

> **Owner**: Paul Prae | **Status**: In Progress
> **Scope**: Everything you need to do before the Autonomize AI interview demo

Each task includes the Claude Code command to run once the human task is done.

---

## After Step 1 (CLI Engine) — v0.1.0

- [ ] **Run UAT**: `make review-all` — verify all 5 cases produce expected results
  - *Then run*: `make test-unit` to confirm automated tests agree
- [ ] **Read rationale quality**: Read each case's rationale aloud — does it sound like a clinical reviewer wrote it?
  - *This is UAT-only* — automated tests check keywords but can't judge clinical tone
- [ ] **Clinical realism check**: Would an ex-Elevance reviewer find the ICD-10 codes and scenarios realistic?
  - *Reference*: `data/sample_pa_cases/README.md` for case definitions

## After Step 2 (REST API) — v0.2.0

- [ ] **Start Docker**: `docker compose up -d && make load-fhir-data`
  - *Then run*: `make test-integration` to verify FHIR server connectivity
- [ ] **Swagger walkthrough**: Open `http://localhost:8000/docs` — try each endpoint
  - *Then run*: `make test-e2e` to run API E2E tests
- [ ] **CLI independence**: `make down && make review` — CLI must work without Docker
  - *This validates the decoupling architecture*

## After Step 3 (Web Dashboard) — v0.3.0

- [ ] **Dashboard smoke test**: `make dev` → open `http://localhost:8000`
  - *Verify*: Case selector loads, 5 cases in demo order, no console errors
- [ ] **Full demo walkthrough**: Submit cases in order 1→4→3→5→2
  - *Target*: 5-6 minutes total, each case < 60 seconds
  - *Narrative*: "Clear approval → missing docs → ambiguous → urgent oncology → denial"
- [ ] **Screen share test**: Start a Teams test call → Share screen → verify all text readable, badges visible
  - *This is UAT-only* — no automated test can verify screen share readability
- [ ] **History panel**: After 5 cases, verify history table shows all 5 with correct determinations
- [ ] **Swagger regression**: Open `http://localhost:8000/docs` — Swagger still works alongside dashboard
- [ ] **CLI regression**: `make review` in a separate terminal — CLI still works independently
- [ ] **Audience test**: Have someone else watch the demo — are badges and rationale clear to a non-technical viewer?

## Before Interview

- [ ] **Architecture prep**: 2-minute overview from `docs/architecture/solution-architecture.md`
- [ ] **Key numbers**: $3.47 savings per automated PA (CAQH 2024), $10.97 provider cost, 93% of physicians report PA delays (AMA 2024)
- [ ] **Anticipated questions**:
  - "Why not auto-deny?" → CMS-0057-F compliance, clinical safety, liability
  - "Why Claude?" → Tool use pattern, FHIR-native reasoning, Anthropic safety alignment
  - "How does this scale?" → Azure Container Apps, Service Bus, PostgreSQL (solution architecture §2)
  - "What about real PHI?" → All data synthetic (Synthea), PHI tokenization before LLM in production
- [ ] **Fallback plan**: If Step 3 fails → demo via Swagger UI (Step 2); if that fails → CLI (Step 1)
- [ ] **Backup recording**: Screenshot or recording of a successful demo run in case of API outage

## Teams Screen Share Prep

- [ ] **This desktop is the demo machine** — no separate laptop needed
- [ ] **Test screen share resolution**: Start a Teams test call → Share screen → confirm text is crisp and readable
- [ ] **Close distracting apps**: Slack, email, personal browser tabs, notifications (Focus Assist ON)
- [ ] **Pre-load browser**: Open `http://localhost:8000` and `http://localhost:8000/docs` in separate tabs before the call
- [ ] **`.env` verified**: Valid API key, Docker running, `make install` done, internet connected

## Infrastructure Prerequisites

- [ ] Docker Desktop installed and running
- [ ] Python 3.12+ installed
- [ ] HAPI FHIR loaded: `docker compose up -d && make load-fhir-data`
