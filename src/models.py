"""Pydantic models for PA requests, determinations, and audit records.

Defines the core data structures used throughout the PA processing pipeline.
All models use Pydantic v2 with strict type validation.

Implementation: Phase 1 (schema) + Phase 3 (request) + Phase 4 (determination).
"""

# TODO Phase 1: Define PARequest model
# Fields: member_id, provider_npi, diagnosis_codes, procedure_codes,
#          service_description, clinical_notes, urgency, lob

# TODO Phase 4: Define PADetermination model
# Fields: request_id, determination (APPROVED | PENDED_FOR_REVIEW),
#          confidence, clinical_rationale, guideline_citations

# TODO Phase 1: Define AuditRecord model
# Fields: id, request_id, event_type, timestamp, details, actor
