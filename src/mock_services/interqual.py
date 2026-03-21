"""Mock InterQual guidelines API.

Simulates InterQual/MCG clinical guidelines matching. Returns mock guideline
match results with clinical criteria and citation references.

Implementation: Phase 2.
"""

# TODO Phase 2: Implement mock guidelines endpoint
#   POST /guidelines/match
#   Request: { "diagnosis_codes": [...], "procedure_codes": [...] }
#   Returns:
#   {
#     "match_found": true,
#     "guideline_id": "IQ-2026-PT-001",
#     "guideline_name": "Physical Therapy — Lumbar Spine",
#     "criteria_met": ["chronic_pain_duration_gt_3mo", "conservative_tx_failed"],
#     "criteria_not_met": [],
#     "recommendation": "APPROVE",
#     "max_sessions": 12,
#     "citation": "InterQual 2026 — Rehabilitation: Physical Therapy, Spine, Criteria Set A"
#   }
