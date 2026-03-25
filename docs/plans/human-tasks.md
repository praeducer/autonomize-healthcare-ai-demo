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

## 1. Infrastructure Prerequisites

- [ ] Python 3.12+ installed
- [ ] Install dependencies:
  - Bash: `make install`
  - PowerShell: `pip install -e ".[dev]"` then `pre-commit install`
- [ ] `.env` created with valid `ANTHROPIC_API_KEY`
- [ ] Docker Desktop installed and running (Step 2+)

## 2. After Step 1 (CLI Engine) — v0.1.0

- [ ] **Run automated tests**:
  - Bash: `make test-unit`
  - PowerShell: `pytest tests/ -m unit -v`
- [ ] **Run UAT**: Follow US-1 through US-5 in [`docs/uat-guide.md`](../uat-guide.md)

## 3. After Step 2 (REST API) — v0.2.0

- [ ] **Start FHIR server**:
  - Bash: `make setup-fhir`
  - PowerShell: `docker compose up -d` then `python -m prior_auth_demo.mock_healthcare_services.load_fhir_data`
- [ ] **Run automated tests**:
  - Bash: `make test-integration && make test-e2e`
  - PowerShell: `pytest tests/ -m integration -v` then `pytest tests/ -m e2e -v --timeout=300`
- [ ] **Run UAT**: Follow US-6, US-7, and Regression section in [`docs/uat-guide.md`](../uat-guide.md)

## 4. After Step 3 (Web Dashboard) — v0.3.0

- [ ] **Start server**:
  - Bash: `make dev`
  - PowerShell: `uvicorn prior_auth_demo.healthcare_api_server:app --reload --port 8000`
- [ ] **Run UAT**: Follow US-8, US-9, and Regression section in [`docs/uat-guide.md`](../uat-guide.md)

## 5. Before Interview

- [ ] **Work through pre-show checklist**: [`docs/interview-prep/pre-show-checklist.md`](../interview-prep/pre-show-checklist.md) (statistics, rehearsal, demo prep, Teams screen share, fallback plan)
- [ ] **Review study guide**: [`docs/interview-prep/study-guide.md`](../interview-prep/study-guide.md) (Q&A, risk awareness, assumptions)
