# Human Tasks — Pre-Interview Checklist

> **Owner**: Paul Prae | **Status**: In Progress
> **Scope**: Everything you need to do before the Autonomize AI interview demo

---

## After Step 1 (CLI Engine) — v0.1.0

- [ ] Run UAT: `make review-all` — verify all 5 cases produce expected results (see `docs/uat-guide.md`)
- [ ] Read each rationale aloud — does it sound like a clinical reviewer wrote it?
- [ ] Check the ICD-10 codes in each case against real clinical scenarios — would an ex-Elevance reviewer find these realistic?

## After Step 2 (REST API) — v0.2.0

- [ ] Start Docker Desktop and run `docker compose up -d && make load-fhir-data`
- [ ] Open `http://localhost:8000/docs` — walk through Swagger UI
- [ ] Submit Case 1 via Swagger POST — verify APPROVED with audit trail
- [ ] Open `http://localhost:8080` — verify HAPI FHIR has patient data
- [ ] Run `make review` — verify CLI still works independently
- [ ] Run `make down && make review` — verify CLI works without Docker

## After Step 3 (Web Dashboard) — v0.3.0

- [ ] Full demo walkthrough: Cases 1→4→3→5→2 in order
- [ ] Time it — target 5-6 minutes total
- [ ] Test at 1920x1080 fullscreen — all text readable on projector?
- [ ] Rehearse the narrative: "Here's a clear approval... now missing info... ambiguous... urgent oncology... denial"
- [ ] Have someone else watch the demo — are the badges and rationale clear to a non-technical viewer?

## Before Interview

- [ ] Prepare 2-minute architecture overview using `docs/architecture/solution-architecture.md`
- [ ] Know the CAQH cost numbers cold: $3.47 savings per automated PA, $10.97 provider cost
- [ ] Be ready to explain: "Why not auto-deny?" → CMS-0057-F, liability, clinical safety
- [ ] Be ready to explain: "Why Claude, not GPT?" → tool use, FHIR-native reasoning, Anthropic safety
- [ ] Be ready to explain: "How does this scale?" → Azure Container Apps, Service Bus, PostgreSQL (see solution architecture §2)
- [ ] Have fallback demo ready: if Step 3 fails, demo via Swagger UI (Step 2); if that fails, CLI (Step 1)
- [ ] Test the `.env` on the demo machine — API key works, model ID is correct

## Infrastructure

- [ ] Docker Desktop installed and running on demo machine
- [ ] Python 3.12+ installed
- [ ] `make install` completed successfully
- [ ] `.env` file has valid `ANTHROPIC_API_KEY`
- [ ] Internet connectivity for Claude API calls during demo
- [ ] Backup: screenshot/recording of a successful demo run in case of API outage
