# User Guide

> **SSOT for**: How to set up and use each interface (CLI, Claude Code, API, Dashboard).

Four ways to interact with the PA review engine. All interfaces call the same engine and produce the same results.

**Related documents:**

- What user stories these interfaces serve: [`docs/user-stories.md`](user-stories.md)
- How to manually test each story: [`docs/uat-guide.md`](uat-guide.md)
- Pre-interview checklist: [`docs/plans/human-tasks.md`](plans/human-tasks.md)

## 1. Claude Code (conversational)

The most natural way to interact during development. Requires Claude Code CLI.

| Command | What it does |
|---------|-------------|
| `/get-pa-cases` | List the 5 sample PA cases |
| `/invoke-pa-review 1` | Review case 1 (lumbar MRI) |
| `/invoke-pa-review keytruda` | Review case 5 by name |
| `/invoke-pa-review-all` | Review all 5 cases with summary |

You can also ask conversationally: "Review the spinal fusion case" or "Run all PA cases and summarize."

## 2. CLI (terminal)

Direct terminal commands. Works standalone — no Docker, no API server needed.

**Bash:**

```bash
make review         # Single case (case 1 — lumbar MRI)
make review-all     # All 5 cases
```

**PowerShell:**

```powershell
# Single case (case 1 — lumbar MRI)
python -m prior_auth_demo.command_line_demo --case data/sample_pa_cases/01_lumbar_mri_clear_approval.json

# All 5 cases
python -m prior_auth_demo.command_line_demo --all
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
python -m prior_auth_demo.mock_healthcare_services.load_fhir_data       # Load 10 Synthea patients

# Subsequent runs — data persists across restarts:
docker compose up -d                                                    # Start HAPI FHIR server

# Then start the API:
uvicorn prior_auth_demo.healthcare_api_server:app --reload --port 8000  # Start FastAPI server
```

Open `http://localhost:8000/docs` for Swagger UI. Key endpoints:

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/prior-auth/review` | Submit a PA case for review |
| GET | `/api/v1/prior-auth/determinations` | List all past determinations |
| GET | `/api/v1/prior-auth/sample-cases` | List available test cases |
| GET | `/health` | System health check |

## 4. Web Dashboard (Step 3+)

**Bash:**

```bash
make up             # Start HAPI FHIR server (or make setup-fhir for first time)
make dev            # Start FastAPI server
```

**PowerShell:**

```powershell
docker compose up -d                                                    # Start HAPI FHIR server
uvicorn prior_auth_demo.healthcare_api_server:app --reload --port 8000  # Start FastAPI server
```

Open `http://localhost:8000`. Select a case from the dropdown and click Submit.

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
pip install -e ".[dev]"          # Install dependencies
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

After Claude calls all tools and analyzes the evidence, it returns a determination with a confidence score (0.0–1.0). The engine then applies routing rules:

| Confidence | Result |
|-----------|--------|
| ≥ 0.85 + APPROVED | **Auto-approved** — clear medical necessity with adequate documentation |
| 0.60–0.84 + APPROVED | **Routed to human reviewer** — approval likely but needs clinical confirmation |
| Any + DENIED | **Preserved as DENIED** — Claude found explicit lack of medical necessity (e.g., cosmetic procedure, diagnosis-procedure mismatch) |
| Any + PENDED_MISSING_INFO | **Preserved** — specific required documentation is absent |
| Any + PENDED_FOR_REVIEW | **Preserved** — clinical picture is ambiguous, needs specialist review |

The system **never auto-denies**. Low confidence always routes to human review. This is a safety design principle, not a Phase 1 limitation.
