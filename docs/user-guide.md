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

```bash
# Single case
make review
# or: python -m prior_auth_demo.command_line_demo --case data/sample_pa_cases/01_lumbar_mri_clear_approval.json

# All 5 cases
make review-all
# or: python -m prior_auth_demo.command_line_demo --all
```

Output is color-coded: green (approved), red (denied), yellow (pended).

## 3. REST API + Swagger (Step 2+)

```bash
make up          # Start HAPI FHIR server
make dev         # Start FastAPI server
```

Open `http://localhost:8000/docs` for Swagger UI. Key endpoints:

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/prior-auth/review` | Submit a PA case for review |
| GET | `/api/v1/prior-auth/determinations` | List all past determinations |
| GET | `/api/v1/prior-auth/sample-cases` | List available test cases |
| GET | `/health` | System health check |

## 4. Web Dashboard (Step 3+)

```bash
make up          # Start HAPI FHIR server
make dev         # Start FastAPI server
```

Open `http://localhost:8000`. Select a case from the dropdown and click Submit.

**Demo order**: 1 (approval) → 4 (missing docs) → 3 (ambiguous) → 5 (urgent) → 2 (denial).

---

## Setup

```bash
make install                     # Install dependencies
cp .env.example .env             # Create config
# Edit .env — add your ANTHROPIC_API_KEY
```

## Architecture

```
You (any interface) → Clinical Review Engine → Claude (with 4 tools)
                                                 ├── ICD-10 lookup (local TSV)
                                                 ├── NPI validation (Luhn-10)
                                                 ├── CMS coverage criteria (local JSON)
                                                 └── Clinical data extraction (from FHIR Bundle)
                                             → ClinicalReviewResult
```

The engine is the same regardless of interface. The CLI, API, and dashboard are thin wrappers. See [`docs/architecture/solution-architecture.md`](architecture/solution-architecture.md) for the full enterprise design.
