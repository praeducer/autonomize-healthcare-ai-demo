# Healthcare Standards

## FHIR R4

- All clinical data structures follow FHIR R4 specification
- Resource IDs follow FHIR format: `{ResourceType}/{id}`
- Bundles use `resourceType: "Bundle"` with `type: "searchset"` for search results
- Include `meta.lastUpdated` on all resources

## Medical Coding

- Diagnosis codes use ICD-10-CM format (e.g., `M54.5` for low back pain)
- Procedure codes use CPT format (e.g., `97110` for therapeutic exercises)
- Provider identifiers use NPI format (10-digit numeric)
- Member IDs follow `MBR-YYYY-NNN` pattern in test data

## Prior Authorization

- PA requests require: member_id, provider_npi, diagnosis_codes, procedure_codes, service_description
- Determinations are: `APPROVED`, `PENDED_FOR_REVIEW`, or `DENIED`
- Confidence threshold for auto-approval: 0.85 (configurable via environment)
- Every determination must have: clinical_rationale, guideline_citations, confidence score
- Complete audit trail for every determination (append-only, never delete)

## Data Privacy

- No real PHI anywhere in the codebase — all test data is synthetic
- Never log member names, SSNs, or full dates of birth
- Audit trail records are append-only (no updates, no deletes)
