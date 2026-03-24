# Shared Build Step Context

> **For Claude Code**: Read this file once before starting any build step. Then read the specific `step-N-*.md` file. All coding standards, FHIR conventions, and architecture rules are in `.claude/rules/` (auto-loaded).

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

1. `make lint` — ruff check + format check
2. `make test-data-quality` — FHIR data validation
3. `make test-unit` — pure logic, no network
4. `make test-integration` — service connectivity (Build Step 2+, needs Docker)
5. `make test-e2e` — full flow with real AI (needs ANTHROPIC_API_KEY)
6. AI architecture review (Claude Code subagent) — code quality, FHIR compliance, security
7. Paul's UAT — manual walkthrough per step's checklist
