# Healthcare Standards

## FHIR R4B

- All clinical data structures follow FHIR R4 specification
- Use `fhir.resources.R4B` Pydantic v2 models (BSD license, PyPI: `fhir.resources>=8.0.0`)
- Resource IDs follow FHIR format: `{ResourceType}/{id}`
- Bundles use `resourceType: "Bundle"` with `type: "searchset"` for search results
- Include `meta.lastUpdated` on all resources

### Key Import Paths

```python
from fhir.resources.R4B.claim import Claim                    # PA request
from fhir.resources.R4B.claimresponse import ClaimResponse    # PA determination
from fhir.resources.R4B.patient import Patient                # Member demographics
from fhir.resources.R4B.coverage import Coverage              # Insurance coverage
from fhir.resources.R4B.condition import Condition            # Diagnoses
from fhir.resources.R4B.procedure import Procedure            # Procedures
from fhir.resources.R4B.practitioner import Practitioner      # Requesting provider
from fhir.resources.R4B.bundle import Bundle                  # FHIR transaction bundles
```

## Da Vinci PAS Convention

- PA requests use FHIR `Claim` with `use: "preauthorization"` (per Da Vinci PAS IG STU 2.0.1)
- PA responses use FHIR `ClaimResponse`

## Medical Coding

- Diagnosis codes use ICD-10-CM format (e.g., `M54.5` for low back pain)
- Procedure codes use CPT format (e.g., `97110` for therapeutic exercises)
- Provider identifiers use NPI format (10-digit numeric)
- Member IDs follow `MBR-YYYY-NNN` pattern in test data
- ICD-10 validation against local CDC data (`data/reference/icd10cm_codes_2026.tsv`)

## Prior Authorization

- PA requests require: member_id, provider_npi, diagnosis_codes, procedure_codes, service_description
- Determinations are: `APPROVED`, `DENIED`, `PENDED_FOR_REVIEW`, `PENDED_MISSING_INFO`
- Confidence threshold for auto-approval: 0.85 (configurable via environment)
- Human review threshold: 0.60 (configurable via environment)
- Every determination must have: clinical_rationale, guideline_citations, confidence score
- Complete audit trail for every determination (append-only, never delete)

## MCP Tool References

- **CMS Coverage DB** (`cms-coverage-db`): LCD/NCD lookups for coverage determinations
- **NPI Registry** (`npi-registry`): Provider validation, specialty, practice info
- Both available via MCP servers configured in `.mcp.json`

## Data Privacy

- No real PHI anywhere in the codebase — all test data is synthetic (Synthea)
- Never log member names, SSNs, or full dates of birth
- Audit trail records are append-only (no updates, no deletes)
