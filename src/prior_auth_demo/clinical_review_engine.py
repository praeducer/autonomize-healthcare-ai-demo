"""Core AI clinical review engine.

Orchestrates Claude tool use to evaluate prior authorization requests
against clinical guidelines and produce structured determinations.
"""

from __future__ import annotations

import csv
import json
import logging
import re
import time
from pathlib import Path
from typing import Any, Literal

import anthropic
import httpx
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.claimresponse import ClaimResponse
from fhir.resources.R4B.reference import Reference
from pydantic import BaseModel, Field

from prior_auth_demo.application_settings import ApplicationSettings

logger = logging.getLogger(__name__)


# --- Data Models ---


class ClinicalReviewResult(BaseModel):
    """Output of the AI clinical review.

    Wraps a FHIR ClaimResponse with demo-specific fields for
    determination routing, confidence scoring, and audit trail.
    """

    determination: Literal["APPROVED", "DENIED", "PENDED_FOR_REVIEW", "PENDED_MISSING_INFO"]
    confidence_score: float = Field(ge=0.0, le=1.0)
    clinical_rationale: str
    guideline_citations: list[str]
    missing_documentation: list[str] | None = None
    fhir_claim_response: ClaimResponse
    review_duration_seconds: float = Field(ge=0.0)


# --- Tool Handler Functions ---

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def lookup_icd10_code(
    code: str,
    tsv_path: Path | None = None,
) -> dict[str, str] | None:
    """Look up an ICD-10-CM code in the local reference TSV file.

    Args:
        code: ICD-10-CM code (e.g., "M54.5").
        tsv_path: Path to the TSV file. Defaults to data/reference/icd10cm_codes_2026.tsv.

    Returns:
        Dict with "code" and "description" keys, or None if not found.
    """
    if tsv_path is None:
        tsv_path = _DATA_DIR / "reference" / "icd10cm_codes_2026.tsv"
    if not tsv_path.exists():
        return None
    with tsv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if row["code"].strip() == code.strip():
                return {"code": row["code"].strip(), "description": row["description"].strip()}
    return None


def validate_npi(npi: str) -> dict[str, Any]:
    """Validate NPI format and Luhn-10 check digit.

    Uses the CMS 80840 prefix for Luhn calculation per
    45 CFR 162.406 standard.
    """
    if not isinstance(npi, str) or len(npi) != 10:
        return {"valid": False, "npi": npi, "reason": "NPI must be exactly 10 digits"}
    if not npi.isdigit():
        return {"valid": False, "npi": npi, "reason": "NPI must contain only numeric digits"}

    # Luhn check with 80840 prefix
    prefixed = "80840" + npi
    total = 0
    for i, ch in enumerate(reversed(prefixed)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d

    if total % 10 != 0:
        return {"valid": False, "npi": npi, "reason": "NPI failed Luhn-10 check digit validation"}

    return {"valid": True, "npi": npi, "reason": "NPI format and check digit valid"}


def check_cms_coverage(
    procedure_code: str,
    json_path: Path | None = None,
) -> dict[str, Any] | None:
    """Look up coverage criteria from local reference JSON.

    Args:
        procedure_code: CPT or HCPCS code (e.g., "72148", "J9271").
        json_path: Path to the JSON file. Defaults to data/reference/cms_coverage_criteria.json.

    Returns:
        Dict with coverage requirements, criteria, and references, or None if not found.
    """
    if json_path is None:
        json_path = _DATA_DIR / "reference" / "cms_coverage_criteria.json"
    if not json_path.exists():
        return None
    with json_path.open(encoding="utf-8") as f:
        data = json.load(f)
    for criteria in data.get("coverage_criteria", []):
        if criteria["procedure_code"] == procedure_code:
            return dict(criteria)
    return None


def retrieve_clinical_data(bundle: Bundle) -> dict[str, Any]:
    """Extract clinical data from the FHIR Bundle for Claude's analysis.

    Extracts Patient demographics, Conditions, Coverage info, Claim details,
    and supporting clinical narratives from the bundle entries.
    """
    result: dict[str, Any] = {
        "patients": [],
        "conditions": [],
        "coverage": [],
        "practitioners": [],
        "claim_details": {},
        "supporting_info": [],
    }

    if not bundle.entry:
        return result

    for entry in bundle.entry:
        if not entry.resource:
            continue
        resource_data = entry.resource.model_dump(exclude_none=True)
        rtype = entry.resource.get_resource_type()

        if rtype == "Patient":
            result["patients"].append(resource_data)
        elif rtype == "Condition":
            result["conditions"].append(resource_data)
        elif rtype == "Coverage":
            result["coverage"].append(resource_data)
        elif rtype == "Practitioner":
            result["practitioners"].append(resource_data)
        elif rtype == "Claim":
            result["claim_details"] = resource_data
            for si in resource_data.get("supportingInfo", []):
                if "valueString" in si:
                    result["supporting_info"].append(si["valueString"])

    return result


async def retrieve_fhir_clinical_data(
    patient_id: str,
    fhir_server_url: str,
) -> dict[str, Any]:
    """Retrieve clinical data from a FHIR server for a patient.

    This is an ADDITIONAL data source that supplements bundle-embedded data.
    Returns empty collections on any error — the engine works without it.
    """
    result: dict[str, Any] = {
        "fhir_conditions": [],
        "fhir_observations": [],
        "fhir_procedures": [],
    }
    try:
        async with httpx.AsyncClient(base_url=fhir_server_url, timeout=10.0) as client:
            for resource_type, key in [
                ("Condition", "fhir_conditions"),
                ("Observation", "fhir_observations"),
                ("Procedure", "fhir_procedures"),
            ]:
                resp = await client.get(f"/{resource_type}", params={"patient": patient_id, "_count": "50"})
                if resp.status_code == 200:
                    bundle_data = resp.json()
                    for entry in bundle_data.get("entry", []):
                        if "resource" in entry:
                            result[key].append(entry["resource"])
    except (httpx.HTTPError, ConnectionError, TimeoutError):
        logger.debug("FHIR server unavailable at %s — using bundle data only", fhir_server_url)
    return result


# --- Confidence Routing ---


def apply_confidence_routing(
    raw_determination: str,
    confidence: float,
    auto_approve_threshold: float = 0.85,
    human_review_threshold: float = 0.60,
) -> str:
    """Apply confidence-based routing to Claude's raw determination.

    Rules:
    - DENIED is always preserved (Claude explicitly determined no medical necessity)
    - PENDED_MISSING_INFO is always preserved
    - PENDED_FOR_REVIEW is always preserved
    - APPROVED with confidence >= auto_approve_threshold stays APPROVED
    - APPROVED with confidence < auto_approve_threshold becomes PENDED_FOR_REVIEW
    - Never auto-deny: low confidence always routes to human review
    """
    if raw_determination in ("DENIED", "PENDED_MISSING_INFO", "PENDED_FOR_REVIEW"):
        return raw_determination

    if raw_determination == "APPROVED":
        if confidence >= auto_approve_threshold:
            return "APPROVED"
        return "PENDED_FOR_REVIEW"

    return "PENDED_FOR_REVIEW"


# --- Claude Tool Definitions ---

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "validate_npi",
        "description": (
            "Validate a healthcare provider's National Provider Identifier (NPI). "
            "Checks that the NPI is exactly 10 digits and passes the Luhn-10 check "
            "digit algorithm per CMS standards. Does NOT verify the provider exists."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "npi": {
                    "type": "string",
                    "description": "The 10-digit NPI number to validate",
                }
            },
            "required": ["npi"],
        },
    },
    {
        "name": "lookup_icd10_code",
        "description": (
            "Look up an ICD-10-CM diagnosis code to get its official description. "
            "Use this to verify diagnosis codes on the claim and understand the "
            "clinical conditions being treated."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "ICD-10-CM code (e.g., 'M54.5', 'C34.11')",
                }
            },
            "required": ["code"],
        },
    },
    {
        "name": "check_cms_coverage",
        "description": (
            "Look up CMS coverage criteria for a procedure code. Returns coverage "
            "requirements, auto-approve criteria, denial criteria, and clinical "
            "guideline references. Use this to evaluate medical necessity against "
            "established coverage policies."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "procedure_code": {
                    "type": "string",
                    "description": "CPT or HCPCS procedure code (e.g., '72148', 'J9271')",
                }
            },
            "required": ["procedure_code"],
        },
    },
    {
        "name": "retrieve_clinical_data",
        "description": (
            "Retrieve the patient's clinical data from the prior authorization "
            "request bundle. Returns patient demographics, active conditions, "
            "insurance coverage details, and supporting clinical narratives. "
            "Call this first to understand the full clinical picture."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]


# --- System Prompt ---

SYSTEM_PROMPT = """\
You are an AI clinical reviewer for a United States health insurance plan. \
Your role is to evaluate prior authorization (PA) requests for medical \
necessity based on clinical evidence and coverage guidelines.

## Your Process

1. **Retrieve Clinical Data**: Always start by calling `retrieve_clinical_data` \
to get the full patient record and clinical context.
2. **Validate Provider**: Call `validate_npi` with the requesting provider's NPI \
to verify it is properly formatted.
3. **Verify Diagnoses**: Call `lookup_icd10_code` for each diagnosis code on the \
claim to confirm the conditions.
4. **Check Coverage Criteria**: Call `check_cms_coverage` with each procedure code \
to get the coverage requirements and guidelines.
5. **Analyze**: Compare the clinical evidence against the coverage criteria. Consider:
   - Does the diagnosis support the requested procedure?
   - Has conservative treatment been attempted where required?
   - Are there any diagnosis-procedure mismatches?
   - Is all required documentation present?
   - Does the clinical evidence meet the specific coverage requirements?

## Determination Rules

- **APPROVED**: Clear medical necessity with adequate documentation meeting all \
coverage criteria.
- **DENIED**: Explicit lack of medical necessity (e.g., cosmetic procedure, \
diagnosis-procedure mismatch, excluded service). You must cite the specific reason.
- **PENDED_FOR_REVIEW**: Clinical picture is ambiguous — some criteria met, some \
gaps exist. Requires specialist human review.
- **PENDED_MISSING_INFO**: Specific required documentation is absent. You must \
list exactly what is missing.

## Important Guidelines

- Never deny a request solely due to low confidence — route uncertain cases to \
human review.
- Always cite specific clinical guidelines and coverage criteria in your rationale.
- For oncology/urgent cases, note the time sensitivity and applicable expedited \
review requirements.
- Your rationale must be at least 2 sentences explaining the clinical reasoning.
- Your confidence score (0.0-1.0) reflects how certain you are in the determination.

## Response Format

After using the tools, provide your determination as a JSON object with these fields:
{
  "determination": "APPROVED|DENIED|PENDED_FOR_REVIEW|PENDED_MISSING_INFO",
  "confidence_score": 0.0-1.0,
  "clinical_rationale": "Detailed clinical reasoning...",
  "guideline_citations": ["Citation 1", "Citation 2"],
  "missing_documentation": ["Item 1", "Item 2"] or null
}"""


# --- Main Engine ---


async def review_prior_auth_request(
    bundle: Bundle,
    settings: ApplicationSettings | None = None,
) -> ClinicalReviewResult:
    """Review a prior authorization request using Claude with tool use.

    Args:
        bundle: FHIR Bundle containing the Claim and supporting resources.
        settings: Application settings. Loaded from environment if not provided.

    Returns:
        ClinicalReviewResult with determination, rationale, and FHIR ClaimResponse.
    """
    if settings is None:
        settings = ApplicationSettings()  # type: ignore[call-arg]

    start_time = time.monotonic()

    claim_data = _extract_claim_from_bundle(bundle)

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key.get_secret_value())

    bundle_json = bundle.model_dump_json(exclude_none=True)
    messages: list[dict[str, Any]] = [
        {
            "role": "user",
            "content": (
                "Please review the following prior authorization request and provide "
                "your clinical determination.\n\n"
                f"FHIR Bundle:\n```json\n{bundle_json}\n```"
            ),
        }
    ]

    # Tool use loop
    max_iterations = 10
    response = None
    for _ in range(max_iterations):
        response = await client.messages.create(
            model=settings.claude_model_id,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,  # type: ignore[arg-type]
            messages=messages,  # type: ignore[arg-type]
        )

        if response.stop_reason == "tool_use":
            assistant_content = response.content
            tool_results: list[dict[str, Any]] = []

            for block in assistant_content:
                if block.type == "tool_use":
                    tool_result = _dispatch_tool(
                        tool_name=block.name,
                        tool_input=block.input,
                        bundle=bundle,
                    )
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(tool_result, default=str),
                        }
                    )

            messages.append({"role": "assistant", "content": assistant_content})
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    if response is None:
        msg = "No response received from Claude"
        raise RuntimeError(msg)

    # Parse Claude's final text response
    final_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            final_text += block.text

    determination_data = _parse_determination(final_text)

    routed_determination = apply_confidence_routing(
        raw_determination=determination_data["determination"],
        confidence=determination_data["confidence_score"],
        auto_approve_threshold=settings.auto_approve_confidence_threshold,
        human_review_threshold=settings.human_review_confidence_threshold,
    )

    elapsed = time.monotonic() - start_time

    claim_response = _build_claim_response(
        claim_data=claim_data,
        determination=routed_determination,
        rationale=determination_data["clinical_rationale"],
    )

    # Cast routed_determination to the Literal type for Pydantic validation
    determination_value: Literal["APPROVED", "DENIED", "PENDED_FOR_REVIEW", "PENDED_MISSING_INFO"] = (
        routed_determination  # type: ignore[assignment]
    )

    return ClinicalReviewResult(
        determination=determination_value,
        confidence_score=determination_data["confidence_score"],
        clinical_rationale=determination_data["clinical_rationale"],
        guideline_citations=determination_data.get("guideline_citations", []),
        missing_documentation=determination_data.get("missing_documentation"),
        fhir_claim_response=claim_response,
        review_duration_seconds=round(elapsed, 2),
    )


# --- Private Helpers ---


def _dispatch_tool(
    tool_name: str,
    tool_input: dict[str, Any],
    bundle: Bundle,
) -> Any:
    """Dispatch a tool call to the appropriate handler."""
    try:
        if tool_name == "validate_npi":
            return validate_npi(tool_input["npi"])
        elif tool_name == "lookup_icd10_code":
            result = lookup_icd10_code(tool_input["code"])
            if result is None:
                return {"code": tool_input["code"], "found": False, "description": "Code not found in reference data"}
            return {**result, "found": True}
        elif tool_name == "check_cms_coverage":
            result = check_cms_coverage(tool_input["procedure_code"])
            if result is None:
                return {
                    "procedure_code": tool_input["procedure_code"],
                    "found": False,
                    "message": "No coverage criteria found",
                }
            return {**result, "found": True}
        elif tool_name == "retrieve_clinical_data":
            return retrieve_clinical_data(bundle)
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    except KeyError as e:
        return {"error": f"Missing required input for {tool_name}: {e}"}


def _extract_claim_from_bundle(bundle: Bundle) -> dict[str, Any]:
    """Extract the Claim resource data from a Bundle."""
    if bundle.entry:
        for entry in bundle.entry:
            if entry.resource and entry.resource.get_resource_type() == "Claim":
                result: dict[str, Any] = entry.resource.model_dump(exclude_none=True)
                return result
    return {}


def _parse_determination(text: str) -> dict[str, Any]:
    """Parse Claude's determination JSON from the response text.

    Handles JSON embedded in markdown code blocks or raw JSON.
    Uses three fallback strategies for robustness.
    """
    # Strategy 1: JSON in markdown code blocks
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        try:
            parsed: dict[str, Any] = json.loads(json_match.group(1))
            return parsed
        except json.JSONDecodeError:
            pass

    # Strategy 2: Find JSON object containing "determination" key
    json_match = re.search(r"\{[^{}]*\"determination\"[^{}]*\}", text, re.DOTALL)
    if json_match:
        try:
            parsed = json.loads(json_match.group(0))
            return parsed
        except json.JSONDecodeError:
            pass

    # Strategy 3: Brace-matching for nested JSON
    brace_start = text.find("{")
    if brace_start >= 0:
        depth = 0
        for i in range(brace_start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        parsed = json.loads(text[brace_start : i + 1])
                        return parsed
                    except json.JSONDecodeError:
                        break

    # Fallback: unparseable response → safe default
    logger.warning("Could not parse Claude's determination JSON. Defaulting to PENDED_FOR_REVIEW.")
    return {
        "determination": "PENDED_FOR_REVIEW",
        "confidence_score": 0.0,
        "clinical_rationale": f"Unable to parse AI response. Raw text: {text[:500]}",
        "guideline_citations": [],
        "missing_documentation": None,
    }


def _build_claim_response(
    claim_data: dict[str, Any],
    determination: str,
    rationale: str,
) -> ClaimResponse:
    """Build a FHIR ClaimResponse from the determination."""
    outcome_map = {
        "APPROVED": "complete",
        "DENIED": "error",
        "PENDED_FOR_REVIEW": "partial",
        "PENDED_MISSING_INFO": "partial",
    }

    return ClaimResponse(
        status="active",
        type=claim_data.get(
            "type",
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/claim-type",
                        "code": "professional",
                    }
                ]
            },
        ),
        use="preauthorization",
        patient=claim_data.get("patient", {"reference": "Patient/unknown"}),
        insurer=Reference(reference="Organization/demo-insurer", display="Demo Health Plan"),
        outcome=outcome_map.get(determination, "partial"),
        disposition=rationale[:200],
        created=claim_data.get("created", "2026-03-24"),
    )
