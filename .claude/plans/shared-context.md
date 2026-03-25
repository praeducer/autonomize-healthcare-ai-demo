# Shared Build Step Context

> **For Claude Code**: Read this file once before starting any build step. Then read the specific `step-N-*.md` file. All coding standards, FHIR conventions, and architecture rules are in `.claude/rules/` (auto-loaded).

## Build Step Status

| Step | Deliverable | Status | Tag |
|------|------------|--------|-----|
| 1 | CLI review engine + 5 PA cases | **COMPLETED** | `v0.1.0` |
| 2 | FastAPI + HAPI FHIR + audit store | **COMPLETED** | `v0.2.0` |
| 3 | Web dashboard (Jinja2 + HTMX) | **COMPLETED** | `v0.3.0` |
| 4 | Docker + Azure deployment | **READY — next step** | — |
| 5 | Azure-native services | Not started (stretch) | — |

---

## Claude Code Automation

Skills, plugins, MCP tools, and hooks are pre-configured to accelerate implementation. Use them — they are pre-authorized in `.claude/settings.local.json`.

### Plugins & Skills Available

| Plugin | Source | When to Use |
|--------|--------|-------------|
| `fhir-developer@healthcare` | Anthropic Healthcare | FHIR R4B resource creation, validation patterns, coding systems (LOINC, SNOMED CT, ICD-10). Invoke for any FHIR data modeling work. |
| `prior-auth-review@healthcare` | Anthropic Healthcare | Prior auth workflow patterns, NPI/ICD-10/CMS checks. Invoke when building the clinical review engine. |
| `context7@claude-plugins-official` | Upstash/Anthropic | Live library docs — add `use context7` to prompts when working with `anthropic` SDK, `fastapi`, `fhir.resources`, `pydantic`, `httpx`, `htmx`. Eliminates hallucinated APIs. |
| `hookify@claude-plugins-official` | Anthropic | Create new behavioral hooks via natural language. Use `/hookify` to add guardrails. |
| `frontend-design` | Anthropic | Dashboard UI design (Build Step 3). Polished, presentation-grade layouts. |
| `feature-dev` | Anthropic | Guided feature development with codebase analysis. Use for each major implementation sub-step. |
| `code-review` / `pr-review-toolkit` | Anthropic | Post-implementation review. Use before each commit gate. |
| `code-simplifier` | Anthropic | Auto-invoked after writing code. Simplifies for clarity and maintainability. |
| `security-guidance` | Anthropic | Healthcare security — PHI protection, audit trail integrity, no SQL injection. |
| `commit-commands` | Anthropic | `/commit` and `/commit-push-pr` for git operations at each commit gate. |

### MCP Tools Available

| MCP Server | Tools | When to Use |
|------------|-------|-------------|
| `cms-coverage-db` | LCD/NCD coverage criteria lookups | Clinical review engine — checking coverage policy for procedures |
| `npi-registry` | Provider NPI validation, specialty lookup | Clinical review engine — validating requesting provider |
| `icd10-codes` | ICD-10-CM/PCS code validation and lookup | Clinical review engine — validating diagnosis and procedure codes |
| `docker-mcp` | Container management (build, run, compose) | Build Steps 2-4 — HAPI FHIR server, app containerization |

### Workflow Skills (superpowers)

| Skill | When to Invoke |
|-------|---------------|
| `brainstorming` | Before designing any new component (engine, API, dashboard) |
| `writing-plans` | When breaking down a build step into sub-tasks |
| `executing-plans` | When executing a written plan with review checkpoints |
| `test-driven-development` | Before writing implementation code — write tests first |
| `systematic-debugging` | When any test fails or unexpected behavior occurs |
| `verification-before-completion` | Before claiming any build step is done — run all verification commands |
| `subagent-driven-development` | When a build step has 2+ independent sub-tasks |
| `dispatching-parallel-agents` | For parallel test writing, parallel file creation |
| `requesting-code-review` | Before each commit gate |
| `finishing-a-development-branch` | After all tests pass at each commit gate |

### Context7 Library Reference (Verified March 24, 2026)

When using Context7 for live documentation, use the exact library identifiers below. Add `use context7` to any prompt, or reference a specific library: `use context7 for /fastapi/fastapi`.

| Library | Context7 ID | Snippets | Notes |
|---------|-------------|----------|-------|
| Anthropic Python SDK | `/anthropics/anthropic-sdk-python` | 127 | Tool use, structured output, streaming |
| FastAPI | `/fastapi/fastapi` | 1,679 | Async endpoints, dependency injection, OpenAPI |
| Pydantic | `/pydantic/pydantic` | 680 | v2 models, validators, serialization |
| pydantic-settings | `/pydantic/pydantic-settings` | 206 | BaseSettings, env var loading, .env files |
| httpx | `/encode/httpx` | 245 | Async HTTP client for FHIR server calls |
| HTMX | `/bigskysoftware/htmx` | 1,747 | hx-post, hx-target, hx-swap, hx-trigger |
| Pico CSS | `/picocss/pico` | 9 | Use `/websites/picocss` (368 snippets) for better coverage |
| Jinja2 | `/pallets/jinja` | 193 | Template inheritance, filters, macros |
| uvicorn | `/kludex/uvicorn` | 150 | ASGI server configuration |
| pytest | `/pytest-dev/pytest` | 771 | Fixtures, markers, parametrize, async |
| pytest-asyncio | `/pytest-dev/pytest-asyncio` | 104 | asyncio_mode, async fixtures |
| aiosqlite | `/omnilib/aiosqlite` | 33 | Async SQLite for audit store |
| polyfactory | `/litestar-org/polyfactory` | 140 | Test data generation from Pydantic models |
| ruff | `/astral-sh/ruff` | 7,045 | Linting rules, formatter configuration |
| FHIR R4 (spec) | `/hl7/fhir` | 5,412 | HL7 FHIR specification (not Python library) |
| fhir.resources | *Not indexed* | -- | Use `fhir-developer@healthcare` plugin instead |

**Usage examples in prompts:**
- `"Build the FastAPI server. use context7 for /fastapi/fastapi and /pydantic/pydantic"`
- `"Implement Claude tool use. use context7 for /anthropics/anthropic-sdk-python"`
- `"Create the HTMX dashboard. use context7 for /bigskysoftware/htmx and /websites/picocss"`

### Automation Hooks (Pre-configured)

| Hook | Trigger | Effect |
|------|---------|--------|
| **Ruff auto-format** | After every Write/Edit of `.py` files | Runs `ruff format` + `ruff check --fix` automatically |

### Standard Workflow Per Build Step

```
1. Invoke /brainstorming (superpowers) — understand requirements
2. Invoke /feature-dev — structured implementation plan
3. Use context7 for library docs: "use context7 for anthropic SDK" etc.
4. Invoke /tdd — write tests before implementation
5. Use fhir-developer skill for FHIR resource work
6. Use prior-auth-review skill for PA workflow logic
7. Use MCP tools (CMS, NPI) in the clinical review engine
8. Ruff auto-formats on save (hook)
9. Invoke /simplify after writing code
10. Run verification: make lint && make test-unit && make test-e2e
11. Invoke /code-review before commit gate
12. Invoke /commit for git operations
```

---

## ClinicalReviewResult Model

The engine's output model — referenced by all build steps:

```python
class ClinicalReviewResult(BaseModel):
    """Output of the AI clinical review — wraps FHIR ClaimResponse with demo-specific fields."""
    determination: Literal["APPROVED", "DENIED", "PENDED_FOR_REVIEW", "PENDED_MISSING_INFO"]
    confidence_score: float  # 0.0 to 1.0
    clinical_rationale: str  # AI-generated reasoning narrative
    guideline_citations: list[str]  # Evidence sources cited
    missing_documentation: list[str] | None  # If pended for missing info
    fhir_claim_response: ClaimResponse  # Full FHIR-compliant response
    review_duration_seconds: float
```

## Step 1 Implementation Notes

- `fhir.resources.R4B` uses `get_resource_type()` method, NOT `resource_type` attribute
- `pydantic-settings` requires lowercase field names for kwargs (e.g., `anthropic_api_key=`, not `ANTHROPIC_API_KEY=`). Env vars are case-insensitive via `case_sensitive=False`.
- `ApplicationSettings()` default constructor loads from `.env` file. In tests, use `_env_file=None` to disable.
- NPI Luhn-10 algorithm: prefix with `80840`, then double every OTHER digit from the RIGHT starting at position 1 (0-indexed). Valid NPIs in demo: `1234567893`, `1528060019`, `1497758544`, `1356425615`, `1649382052`.
- CMS coverage criteria stored locally in `data/reference/cms_coverage_criteria.json` (not runtime MCP calls). MCP servers are Claude Code protocol, not available to the Python app at runtime.
- Anthropic SDK tool use: `tools` and `messages` params need `# type: ignore[arg-type]` for mypy strict mode (SDK type stubs are looser than strict mypy expects).
- `polyfactory` cannot auto-generate valid FHIR models. Pre-build a `ClaimResponse` and assign as class attribute override on the factory.

## Step 2 Implementation Notes

- `httpx.ASGITransport` does NOT reliably trigger FastAPI lifespan events. Use lazy initialization (`_ensure_initialized()`) for module-level state like settings and audit store.
- HAPI FHIR image pinned to `v7.6.0` (not `:latest`) for reproducibility. Uses H2 file-based storage.
- FHIR data loader uses PUT (not POST) with explicit resource IDs for idempotent loading.
- Synthea data loads in dependency order: Organization → Practitioner → Patient → everything else.
- Audit store uses `aiosqlite.Row` row factory for `dict(row)` conversion. Set in `init_db()`.
- The `retrieve_fhir_clinical_data()` function catches ALL exceptions (including `httpx.HTTPError`) and returns empty dict — CLI works without Docker.
- E2E tests use result caching (`_result_cache` dict) to avoid redundant API calls. One Claude call per case.

## Stakeholder Review Protocol

After each build step, simulate critical feedback from interview personas before proceeding:

| Persona | Focus Area | Key Questions |
|---------|-----------|---------------|
| **VP Engineering** | Architecture, scalability, code quality | "Does this architecture scale? Is the code production-grade?" |
| **Chief Medical Officer** | Clinical accuracy, safety, compliance | "Are the determinations clinically appropriate? What about auto-denial risk?" |
| **CISO** | Security, PHI, audit trail | "Where is PHI? Is the audit trail tamper-proof? Any injection vectors?" |
| **Product Manager** | Demo quality, user experience | "Can I present this to a client? Does it tell a compelling story?" |

Address their feedback in the plan before starting the next step. See `docs/plans/human-tasks.md` for Paul's pre-interview checklist.

## Healthcare Service Contracts

### Real Services

**HAPI FHIR Server** (Build Step 2+):
```
GET http://localhost:8080/fhir/Patient?identifier={member_id}
GET http://localhost:8080/fhir/Condition?patient={patient_id}
GET http://localhost:8080/fhir/Observation?patient={patient_id}
GET http://localhost:8080/fhir/Procedure?patient={patient_id}
```

**CMS Coverage Database** — LCD/NCD lookups (MCP server, see `.mcp.json`)
**NPI Registry** — provider validation (MCP server, see `.mcp.json`)

**ICD-10 Validation** — local CDC data:
- File: `data/reference/icd10cm_codes_2026.tsv`
- Source: `https://ftp.cdc.gov/pub/health_statistics/nchs/publications/ICD10CM/2026/`

### Mock Service (One Only)

**Member Eligibility** — no open-source payer eligibility API exists:
```
POST /mock/eligibility/check
  Input: member_id, service_date, procedure_code
  Output: FHIR CoverageEligibilityResponse (eligible: true/false, plan_type, copay)
```
~30 lines. Returns realistic FHIR response. Production would connect to Payer Core System (TriZetto Facets, QNXT, etc.).

## Version Control Strategy

Each build step produces a tagged release and release branch. If a later step fails, revert to the last working release.

| Step | Git Tag | Release Branch | Fallback Demo |
|------|---------|----------------|---------------|
| 1 | `v0.1.0` | `release/step-1-core-engine` | CLI terminal |
| 2 | `v0.2.0` | `release/step-2-api-service` | Swagger UI |
| 3 | `v0.3.0` | `release/step-3-web-dashboard` | Web dashboard (local) |
| 4 | `v0.4.0` | `release/step-4-azure-deploy` | Live cloud URL |
| 5 | `v0.5.0` | `release/step-5-managed-services` | Azure-native |

**Commit gate commands** (run at the end of every build step):
```bash
git add -A
git commit -m "Step N: <description>"
git tag -a v0.N.0 -m "Step N: <description>"
git checkout -b release/step-N-<name>
git checkout main
git push origin main --tags
git push origin release/step-N-<name>
```

## Verification Protocol

Every build step follows this test sequence. All automated tests must pass before Paul's UAT.

1. Lint — bash: `make lint` / PowerShell: `ruff check src/prior_auth_demo/ tests/ && ruff format --check src/prior_auth_demo/ tests/ && mypy src/prior_auth_demo/`
2. Data quality — bash: `make test-data-quality` / PowerShell: `pytest tests/test_data_quality.py -v`
3. Unit tests — bash: `make test-unit` / PowerShell: `pytest tests/ -m unit -v`
4. Integration tests (Build Step 2+, needs Docker) — bash: `make test-integration` / PowerShell: `pytest tests/ -m integration -v`
5. E2E tests (needs ANTHROPIC_API_KEY) — bash: `make test-e2e` / PowerShell: `pytest tests/ -m e2e -v --timeout=300`
6. AI architecture review (Claude Code subagent) — code quality, FHIR compliance, security
7. Paul's UAT — manual walkthrough per step's checklist
