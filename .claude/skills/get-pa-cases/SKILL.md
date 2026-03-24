---
name: get-pa-cases
description: Use when the user asks what PA cases are available, wants to see the case list, or asks about test scenarios
---

List the available prior authorization test cases:

| # | Case | Diagnosis | Procedure | Expected |
|---|------|-----------|-----------|----------|
| 1 | Lumbar MRI | M54.5, M54.41 (back pain, sciatica) | CPT 72148 | APPROVED |
| 2 | Rhinoplasty | L57.0 (actinic keratosis — mismatch) | CPT 30400 | DENIED |
| 3 | Spinal Fusion | M47.816, M48.06, E11.9 | CPT 22612+ | PENDED_FOR_REVIEW |
| 4 | Humira | M05.79 (rheumatoid arthritis) | HCPCS J0135 | PENDED_MISSING_INFO |
| 5 | Keytruda | C34.11, C77.1 (lung cancer) | HCPCS J9271 | APPROVED (urgent) |

Then say: Use `/invoke-pa-review <number or name>` to review a case, or `/invoke-pa-review-all` to review all 5.
