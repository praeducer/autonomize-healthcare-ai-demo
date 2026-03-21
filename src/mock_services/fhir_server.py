"""Mock FHIR R4 server.

Simulates AWS HealthLake / EMR FHIR endpoints. Returns mock FHIR R4 Bundles
for Patient, Condition, and Observation resources with realistic healthcare data.

Implementation: Phase 2.
"""

# TODO Phase 2: Implement mock FHIR endpoints
#   GET /fhir/Patient/{id} — Patient resource with demographics
#   GET /fhir/Condition?patient={id} — Condition Bundle (ICD-10 coded)
#   GET /fhir/Observation?patient={id} — Observation Bundle (vitals, labs)
#
# All responses should use FHIR R4 Bundle format with:
#   - resourceType, id, meta (lastUpdated)
#   - Realistic ICD-10 codes (e.g., M54.5 for low back pain)
#   - Realistic LOINC codes for observations
