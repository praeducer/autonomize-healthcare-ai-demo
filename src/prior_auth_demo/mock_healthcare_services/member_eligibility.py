"""Mock member eligibility service.

Returns FHIR CoverageEligibilityResponse for demo PA cases.
All members are eligible — production would connect to a Payer Core System.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter

router = APIRouter(tags=["Mock Services"])


@router.post("/check")
async def check_eligibility(request: dict[str, Any]) -> dict[str, Any]:
    """Check member eligibility. Returns FHIR CoverageEligibilityResponse.

    All demo members are eligible. This mock replaces what would be
    a Payer Core System integration (TriZetto Facets, QNXT, etc.).
    """
    member_id = request.get("member_id", "unknown")

    return {
        "resourceType": "CoverageEligibilityResponse",
        "status": "active",
        "purpose": ["auth-requirements"],
        "patient": {"reference": f"Patient/{member_id}"},
        "created": date.today().isoformat(),
        "insurer": {"reference": "Organization/demo-insurer", "display": "Demo Health Plan"},
        "insurance": [
            {
                "coverage": {"reference": f"Coverage/{member_id}"},
                "inforce": True,
                "item": [
                    {
                        "category": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/ex-benefitcategory",
                                    "code": "30",
                                    "display": "Health Benefit Plan Coverage",
                                }
                            ]
                        },
                        "benefit": [
                            {
                                "type": {
                                    "coding": [
                                        {
                                            "system": "http://terminology.hl7.org/CodeSystem/benefit-type",
                                            "code": "benefit",
                                        }
                                    ]
                                },
                                "allowedString": "Eligible — prior authorization required",
                            }
                        ],
                    }
                ],
            }
        ],
    }
