# AI-Driven Prior Authorization Demo

> Proof-of-concept demonstrating AI-driven prior authorization review
> using Claude, FHIR R4, and evidence-based clinical guidelines.
> Built for the [Autonomize AI](https://autonomize.ai/) Solutions Architect
> interview assignment.

**Author**: [Paul Prae](https://www.paulprae.com) — Modular Earth LLC

## Architecture Overview

```mermaid
flowchart LR
    subgraph "Providers"
        PROV["Healthcare Providers<br/>Physicians, Facilities"]
    end

    subgraph "Health Plan Systems"
        CORE["Payer Core System<br/>Enrollment, Benefits, Contracts"]
        CLIN["Clinical Data Sources<br/>FHIR R4 + Legacy DBs"]
    end

    subgraph "Autonomize AI Platform"
        PA_COPILOT["PA Copilot<br/>AI-Driven Review Engine"]
    end

    subgraph "Regulatory"
        CMS["CMS / State Regulators<br/>Compliance Reporting"]
    end

    PROV -->|"PA Requests<br/>Fax, Portal, X12 278"| PA_COPILOT
    CORE -->|"Eligibility + Benefits<br/>REST API"| PA_COPILOT
    CLIN -->|"Clinical Records<br/>FHIR R4 API"| PA_COPILOT
    PA_COPILOT -->|"Determinations<br/>REST API"| CORE
    PA_COPILOT -->|"Compliance Metrics<br/>CMS-0057-F"| CMS
    PA_COPILOT -->|"Status Updates<br/>Portal / Fax"| PROV
```

The full enterprise architecture covers 10 components across 5 layers — ingestion, integration, AI engine, human review, and response — all on HIPAA-compliant Azure-native services.

- [Solution Architecture](docs/architecture/solution-architecture.md) — master reference
- [Presentation Deck](docs/presentation/presentation.md) — 11 slides, priority-tiered
- [Architecture Diagrams](docs/architecture/diagrams/) — 6 progressive views

## Quick Start

```bash
make install        # Install dependencies + pre-commit hooks
make review         # Run a single PA case through AI review (CLI)
make review-all     # Run all 5 PA cases
make dev            # Start the FastAPI server (Build Step 2+)
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Engine | Anthropic SDK + Claude Sonnet 4.6 |
| Clinical Data | FHIR R4 (fhir.resources R4B) + HAPI FHIR Server |
| PA Standard | Da Vinci PAS IG (FHIR Claim/ClaimResponse) |
| Reference Data | CMS Coverage DB (MCP), NPI Registry (MCP), CDC ICD-10-CM |
| API | FastAPI + Pydantic v2 |
| Web UI | Jinja2 + HTMX + Pico CSS |
| Audit | SQLite (append-only) |
| Config | pydantic-settings |

## Project Structure

```
src/prior_auth_demo/
├── clinical_review_engine.py         # Core AI: Claude + tool use -> determination
├── command_line_demo.py              # CLI entry point
├── healthcare_api_server.py          # FastAPI REST API
├── application_settings.py           # Environment configuration
├── determination_audit_store.py      # SQLite audit trail
├── mock_healthcare_services/         # Mock payer services
└── web_dashboard/                    # Jinja2 + HTMX dashboard
```

## Demo Build Steps

> "Build Step" = demo build milestones. "Phase" = enterprise delivery roadmap (see [Progressive Delivery](docs/presentation/presentation.md#slide-9-progressive-delivery)). This entire demo is Phase 0.

| Step | Deliverable | Tag |
|------|------------|-----|
| 0 | Repo preparation | v0.0.1 |
| 1 | CLI review engine + 5 PA cases | v0.1.0 |
| 2 | FastAPI + HAPI FHIR + audit store | v0.2.0 |
| 3 | Web dashboard (Jinja2 + HTMX) | v0.3.0 |
| 4 | Docker + Azure deployment | v0.4.0 |
| 5 | Azure-native services | v0.5.0 |

Each build step is independently demo-able. Decision gates between steps use real performance data.

## Documentation

All deliverables in [docs/](docs/README.md):

| Document | What it covers |
|----------|---------------|
| [User Guide](docs/user-guide.md) | How to use each interface (CLI, Claude Code, API, Dashboard) |
| [User Stories](docs/user-stories.md) | 9 user stories with roles, acceptance criteria, and build step |
| [UAT Guide](docs/uat-guide.md) | Manual acceptance testing organized by user story |
| [Human Tasks](docs/plans/human-tasks.md) | Pre-interview checklist — tests, infrastructure, prep |

| Section | Contents |
|---------|----------|
| [Architecture](docs/architecture/) | Solution design, research context, requirements traceability, diagrams |
| [Presentation](docs/presentation/) | Slide deck, speaker script, demo script |
| [Interview Prep](docs/interview-prep/) | Study guide, Q&A reference, pre-show checklist, panel email |
| [Inputs](docs/inputs/) | Assignment, stakeholder profiles, job description |
| [Plans](docs/plans/) | Design doc, human tasks checklist |

## License

MIT — see [LICENSE](LICENSE)
