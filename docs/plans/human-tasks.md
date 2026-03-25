# Human Tasks — Pre-Interview Checklist

> **SSOT for**: The ordered checklist of human tasks to complete before the Autonomize AI interview.
>
> **Owner**: Paul Prae | **Status**: In Progress

**Related documents (SSOT for their domains):**

- Interface setup and commands: [`docs/user-guide.md`](../user-guide.md)
- Manual test procedures by user story: [`docs/uat-guide.md`](../uat-guide.md)
- User story definitions: [`docs/user-stories.md`](../user-stories.md)
- Interview prep (statistics, Q&A, risks): [`docs/interview-prep/`](../interview-prep/)
- Case definitions and expected outcomes: [`data/sample_pa_cases/README.md`](../../data/sample_pa_cases/README.md)

---

## After Step 1 (CLI Engine) — v0.1.0

- [ ] **Run automated tests**: `make test-unit`
- [ ] **Run UAT**: Follow US-1 through US-5 in [`docs/uat-guide.md`](../uat-guide.md)

## After Step 2 (REST API) — v0.2.0

- [ ] **Start Docker**: `make setup-fhir` (starts HAPI FHIR, waits for health check, loads Synthea data)
- [ ] **Run automated tests**: `make test-integration && make test-e2e`
- [ ] **Run UAT**: Follow US-6, US-7, and Regression section in [`docs/uat-guide.md`](../uat-guide.md)

## After Step 3 (Web Dashboard) — v0.3.0

- [ ] **Start server**: `make dev`
- [ ] **Run UAT**: Follow US-8, US-9, and Regression section in [`docs/uat-guide.md`](../uat-guide.md)

## Before Interview

For key statistics, Q&A preparation, and risk awareness, see [`docs/interview-prep/pre-show-checklist.md`](../interview-prep/pre-show-checklist.md) and [`docs/interview-prep/study-guide.md`](../interview-prep/study-guide.md).

- [ ] **Architecture prep**: 2-minute overview from [`docs/architecture/solution-architecture.md`](../architecture/solution-architecture.md)
- [ ] **Review key numbers**: CAQH 2024 and AMA 2024 statistics — verified in [`docs/interview-prep/pre-show-checklist.md`](../interview-prep/pre-show-checklist.md)
- [ ] **Review anticipated questions**: See Q&A section in [`docs/interview-prep/study-guide.md`](../interview-prep/study-guide.md)
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
- [ ] HAPI FHIR loaded: `make setup-fhir`
