# User Guide

> **SSOT for**: Setup, commands, tool descriptions, and architecture for all interfaces (CLI, Claude Code, API, Dashboard).
>
> Other docs reference this file for commands and technical details — update here first.

Four ways to interact with the PA review engine. All interfaces call the same engine and produce the same results.

**Related documents:**

- What user stories these interfaces serve: [`docs/user-stories.md`](user-stories.md)
- How to manually test each story: [`docs/uat-guide.md`](uat-guide.md)
- Pre-interview checklist: [`docs/plans/human-tasks.md`](plans/human-tasks.md)
- Confidence thresholds and determination rules: [`.claude/rules/healthcare-standards.md`](../.claude/rules/healthcare-standards.md)
- Acronyms and terminology: [`docs/interview-prep/study-guide.md`](interview-prep/study-guide.md#5-vocabulary-flashcards)
- Data flow and service boundaries: [`.claude/rules/architecture.md`](../.claude/rules/architecture.md)
- PA case definitions and expected outcomes: [`data/sample_pa_cases/README.md`](../data/sample_pa_cases/README.md)

## 1. Claude Code (conversational)

The most natural way to interact during development. Requires Claude Code CLI.

| Command | What it does |
|---------|-------------|
| `/get-pa-cases` | List available PA cases (reads from `data/sample_pa_cases/README.md`) |
| `/inspect-pa-case 1` | Show case 1's clinical data — no AI, no API calls |
| `/invoke-pa-review 1` | Run AI review on case 1 (lumbar MRI) |
| `/invoke-pa-review keytruda` | Run AI review on case 5 by name |
| `/invoke-pa-review-all` | Run AI review on all cases and show summary |

You can also ask conversationally: "Review the spinal fusion case" or "Run all PA cases and summarize."

## 2. CLI (terminal)

Direct terminal commands. Works standalone — no Docker, no API server needed.

**Bash:**

```bash
make review         # Run AI review on case 1 (lumbar MRI)
make review-all     # Run AI review on all 5 cases
```

**PowerShell:**

```powershell
# Inspect a case's clinical data (no AI, no API calls)
uv run python -m prior_auth_demo.command_line_demo --inspect data/sample_pa_cases/01_lumbar_mri_clear_approval.json

# Run AI review on a single case
uv run python -m prior_auth_demo.command_line_demo --case data/sample_pa_cases/01_lumbar_mri_clear_approval.json

# Run AI review on all 5 cases
uv run python -m prior_auth_demo.command_line_demo --all
```

Output is color-coded: green (approved), red (denied), yellow (pended).

## 3. REST API + Swagger (Step 2+)

**Bash:**

```bash
make setup-fhir     # First time: start HAPI FHIR + load Synthea patients
make up             # Subsequent runs: data persists across restarts
make dev            # Start FastAPI server
```

**PowerShell:**

```powershell
# First time — start FHIR server + load patient data:
docker compose up -d                                                    # Start HAPI FHIR (Docker)
uv run python -m prior_auth_demo.mock_healthcare_services.load_fhir_data       # Load 10 Synthea patients

# Subsequent runs — data persists across restarts:
docker compose up -d                                                    # Start HAPI FHIR server

# Then start the API:
uv run uvicorn prior_auth_demo.healthcare_api_server:app --reload --port 8000  # Start FastAPI server
```

Open `http://localhost:8000/docs` for Swagger UI. Endpoints are numbered in demo order:

| # | Method | Path | Description |
|---|--------|------|-------------|
| 1 | GET | `/health` | Check system health — call this first |
| 2 | GET | `/api/v1/prior-auth/sample-cases` | List available test cases |
| 3 | GET | `/api/v1/prior-auth/sample-cases/{name}` | Get a case's FHIR Bundle payload |
| 4 | POST | `/api/v1/prior-auth/review` | Submit a Bundle for AI review (pre-filled example in Swagger) |
| 5 | GET | `/api/v1/prior-auth/determinations` | View audit trail of all past reviews |

The POST /review endpoint has a **pre-filled example payload** — click "Try it out" and Execute to run a review immediately.

## 4. Web Dashboard (Step 3+)

**Bash:**

```bash
make up             # Start HAPI FHIR server (or make setup-fhir for first time)
make dev            # Start FastAPI server
```

**PowerShell:**

```powershell
docker compose up -d                                                    # Start HAPI FHIR server
uv run uvicorn prior_auth_demo.healthcare_api_server:app --reload --port 8000  # Start FastAPI server
```

Open `http://localhost:8000/dashboard` (or `http://localhost:8000/`). Select a case from the dropdown and click Submit.

**Demo order**: 1 (approval) → 4 (missing docs) → 3 (ambiguous) → 5 (urgent) → 2 (denial).

---

## Setup

**Bash:**

```bash
make install                     # Install dependencies + pre-commit hooks
cp .env.example .env             # Create config
# Edit .env — add your ANTHROPIC_API_KEY
```

**PowerShell:**

```powershell
uv sync                          # Install dependencies
pre-commit install               # Install pre-commit hooks
Copy-Item .env.example .env      # Create config
# Edit .env — add your ANTHROPIC_API_KEY
```

## Architecture

```
You (any interface) → Clinical Review Engine → Claude (with 4 tools)
                                                 ├── retrieve_clinical_data  (FHIR Bundle → structured patient data)
                                                 ├── validate_npi            (Luhn-10 check digit validation)
                                                 ├── lookup_icd10_code       (CDC ICD-10-CM 2026 reference)
                                                 └── check_cms_coverage      (CMS LCD/NCD coverage criteria)
                                             → ClinicalReviewResult → Confidence Routing → Determination
```

The engine is the same regardless of interface. The CLI, API, and dashboard are thin wrappers. See [`docs/architecture/solution-architecture.md`](architecture/solution-architecture.md) for the full enterprise design.

### How Claude Reviews a PA Request

Claude receives the FHIR (Fast Healthcare Interoperability Resources) Bundle and calls 4 tools in sequence — like a human clinical reviewer consulting different reference systems — to gather evidence before rendering a determination.

| Tool | What It Does | Why It's Necessary |
|------|-------------|-------------------|
| **`retrieve_clinical_data`** | Extracts Patient demographics, Conditions (diagnoses), Coverage (insurance), Practitioner info, Claim details, and supporting clinical narratives from the FHIR R4 Bundle. | Claude needs the full clinical picture before evaluating anything. Called first on every review. |
| **`validate_npi`** | Validates the requesting provider's NPI (National Provider Identifier) — a unique 10-digit number assigned by CMS (Centers for Medicare & Medicaid Services) to every US healthcare provider. Uses the Luhn-10 check digit algorithm with the CMS 80840 prefix per 45 CFR 162.406. | Catches invalid or mistyped provider identifiers. A real payer system would also verify the provider exists and is in-network. |
| **`lookup_icd10_code`** | Looks up ICD-10-CM (International Classification of Diseases, 10th Revision, Clinical Modification) diagnosis codes against the 2026 CDC (Centers for Disease Control and Prevention) reference data. Returns the official description for each code (e.g., `M54.5` → "Low back pain"). | Verifies that diagnosis codes on the claim are valid and helps Claude understand the clinical conditions being treated. |
| **`check_cms_coverage`** | Looks up CMS coverage criteria by CPT (Current Procedural Terminology) or HCPCS (Healthcare Common Procedure Coding System) procedure code. Returns coverage requirements, auto-approve criteria, denial criteria, and clinical guideline references. | The core medical necessity evaluation — does this patient's clinical picture meet the established coverage criteria for this procedure? |

### Confidence-Based Routing

After Claude calls all tools and analyzes the evidence, it returns a determination with a confidence score (0.0–1.0). The engine then applies routing rules (thresholds defined in [healthcare-standards.md](../.claude/rules/healthcare-standards.md)):

| Confidence | Result |
|-----------|--------|
| ≥ 0.85 + APPROVED | **Auto-approved** — clear medical necessity with adequate documentation |
| 0.60–0.84 + APPROVED | **Routed to human reviewer** — approval likely but needs clinical confirmation |
| Any + DENIED | **Preserved as DENIED** — Claude found explicit lack of medical necessity (e.g., cosmetic procedure, diagnosis-procedure mismatch) |
| Any + PENDED_MISSING_INFO | **Preserved** — specific required documentation is absent |
| Any + PENDED_FOR_REVIEW | **Preserved** — clinical picture is ambiguous, needs specialist review |

The system **never auto-denies**. Low confidence always routes to human review. This is a safety design principle, not a Phase 1 limitation.
