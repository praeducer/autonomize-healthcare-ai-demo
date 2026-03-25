"""CLI entry point for prior authorization review demo.

Usage:
    python -m prior_auth_demo.command_line_demo --case data/sample_pa_cases/01_lumbar_mri_clear_approval.json
    python -m prior_auth_demo.command_line_demo --all
    python -m prior_auth_demo.command_line_demo --inspect data/sample_pa_cases/01_lumbar_mri_clear_approval.json
"""

from __future__ import annotations

import argparse
import asyncio
import io
import json
import sys
import textwrap
import threading
import time
from pathlib import Path

# Ensure stdout handles Unicode on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from fhir.resources.R4B.bundle import Bundle

from prior_auth_demo.application_settings import ApplicationSettings
from prior_auth_demo.clinical_review_engine import (
    ClinicalReviewResult,
    review_prior_auth_request,
)

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"

SAMPLE_CASES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "sample_pa_cases"

# Human-readable case labels
CASE_LABELS: dict[str, str] = {
    "01_lumbar_mri_clear_approval.json": "Lumbar MRI — Conservative Treatment Failure",
    "02_cosmetic_rhinoplasty_denial.json": "Rhinoplasty — Cosmetic (Diagnosis Mismatch)",
    "03_spinal_fusion_complex_review.json": "Spinal Fusion — Complex (Ambiguous Criteria)",
    "04_humira_missing_documentation.json": "Humira — Missing Step Therapy Documentation",
    "05_keytruda_urgent_oncology.json": "Keytruda — Urgent Oncology (NSCLC)",
}


def _case_label(filename: str) -> str:
    """Get a human-readable label for a case filename."""
    return CASE_LABELS.get(Path(filename).name, Path(filename).name)


def format_determination_badge(determination: str) -> str:
    """Format a determination as a color-coded badge string."""
    color_map = {
        "APPROVED": GREEN,
        "DENIED": RED,
        "PENDED_FOR_REVIEW": YELLOW,
        "PENDED_MISSING_INFO": YELLOW,
    }
    color = color_map.get(determination, RESET)
    return f"{BOLD}{color}[{determination}]{RESET}"


def _spinner(stop_event: threading.Event, label: str) -> None:
    """Show a spinner while waiting for the AI review."""
    frames = [".", "..", "...", "   "]
    i = 0
    start = time.monotonic()
    while not stop_event.is_set():
        elapsed = time.monotonic() - start
        sys.stderr.write(f"\r{DIM}  {label}{frames[i % len(frames)]} ({elapsed:.0f}s){RESET}  ")
        sys.stderr.flush()
        i += 1
        stop_event.wait(0.5)
    sys.stderr.write("\r" + " " * 60 + "\r")
    sys.stderr.flush()


def print_result(result: ClinicalReviewResult, case_path: str) -> None:
    """Pretty-print a clinical review result to the terminal."""
    label = _case_label(case_path)
    width = 70

    print(f"\n{'=' * width}")
    print(f"{BOLD}  {label}{RESET}")
    print(f"{'=' * width}")
    print(f"  {BOLD}Determination:{RESET}  {format_determination_badge(result.determination)}")
    print(f"  {BOLD}Confidence:{RESET}     {result.confidence_score:.0%}")
    print(f"  {BOLD}Review Time:{RESET}    {result.review_duration_seconds:.1f}s")

    if result.determination in ("PENDED_FOR_REVIEW", "PENDED_MISSING_INFO"):
        print(f"\n  {YELLOW}{BOLD}>> Would route to human clinical reviewer{RESET}")

    # Wrap rationale to terminal width for readability
    print(f"\n{BOLD}  Clinical Rationale{RESET}")
    print(f"  {'-' * (width - 4)}")
    wrapped = textwrap.fill(result.clinical_rationale, width=width - 4)
    for line in wrapped.split("\n"):
        print(f"  {line}")

    print(f"\n{BOLD}  Guideline Citations{RESET}")
    print(f"  {'-' * (width - 4)}")
    for citation in result.guideline_citations:
        wrapped_cite = textwrap.fill(citation, width=width - 6)
        first = True
        for line in wrapped_cite.split("\n"):
            prefix = "  * " if first else "    "
            print(f"{prefix}{line}")
            first = False

    if result.missing_documentation:
        print(f"\n  {YELLOW}{BOLD}Missing Documentation{RESET}")
        print(f"  {'-' * (width - 4)}")
        for item in result.missing_documentation:
            print(f"  {YELLOW}* {item}{RESET}")

    print(f"{'=' * width}\n")


async def review_single_case(case_path: str, settings: ApplicationSettings) -> ClinicalReviewResult:
    """Load and review a single PA case from a JSON file."""
    path = Path(case_path)
    if not path.exists():
        print(f"{RED}Error: File not found: {case_path}{RESET}", file=sys.stderr)
        sys.exit(1)

    label = _case_label(case_path)
    print(f"\n{CYAN}{BOLD}Submitting:{RESET} {label}")

    # Start spinner
    stop = threading.Event()
    spinner = threading.Thread(target=_spinner, args=(stop, "AI clinical review in progress"), daemon=True)
    spinner.start()

    with path.open() as f:
        data = json.load(f)

    bundle = Bundle.model_validate(data)
    result = await review_prior_auth_request(bundle, settings)

    # Stop spinner
    stop.set()
    spinner.join()

    print_result(result, case_path)
    return result


async def review_all_cases(settings: ApplicationSettings) -> list[ClinicalReviewResult]:
    """Review all PA cases in the sample_pa_cases directory."""
    case_files = sorted(SAMPLE_CASES_DIR.glob("*.json"))
    if not case_files:
        print(f"{RED}Error: No JSON files found in {SAMPLE_CASES_DIR}{RESET}", file=sys.stderr)
        sys.exit(1)

    print(f"\n{BOLD}{CYAN}{'=' * 70}")
    print("  Prior Authorization Review — AI-Driven Clinical Decision Support")
    print(f"{'=' * 70}{RESET}")
    print(f"  Reviewing {len(case_files)} PA cases using Claude with FHIR R4 tool use\n")

    results = []
    for case_file in case_files:
        result = await review_single_case(str(case_file), settings)
        results.append(result)

    # Print summary
    print(f"{BOLD}{CYAN}{'=' * 70}")
    print(f"  SUMMARY — {len(results)} cases reviewed")
    print(f"{'=' * 70}{RESET}")
    for case_file, result in zip(case_files, results):
        label = _case_label(str(case_file))
        print(f"  {format_determination_badge(result.determination):45s} {result.confidence_score:.0%}  {label}")
    print(f"{CYAN}{'=' * 70}{RESET}\n")
    return results


def inspect_case(case_path: str) -> None:
    """Inspect a PA case's clinical data without running AI review.

    Parses the FHIR Bundle and displays the clinical data that Claude
    would analyze: patient, diagnoses, procedures, provider, and
    supporting narratives. No API calls — purely local data extraction.
    """
    from prior_auth_demo.clinical_review_engine import lookup_icd10_code, retrieve_clinical_data

    path = Path(case_path)
    if not path.exists():
        print(f"{RED}Error: File not found: {case_path}{RESET}", file=sys.stderr)
        sys.exit(1)

    label = _case_label(case_path)
    width = 70

    with path.open() as f:
        data = json.load(f)

    bundle = Bundle.model_validate(data)
    clinical = retrieve_clinical_data(bundle)

    print(f"\n{'=' * width}")
    print(f"{BOLD}  {label}{RESET}")
    print(f"  {DIM}Clinical data from FHIR R4 Bundle (no AI review){RESET}")
    print(f"{'=' * width}")

    # Patient
    for patient in clinical["patients"]:
        name_parts = []
        for name in patient.get("name", []):
            given = " ".join(name.get("given", []))
            family = name.get("family", "")
            name_parts.append(f"{given} {family}".strip())
        name_str = ", ".join(name_parts) if name_parts else "Unknown"
        print(f"\n{BOLD}  Patient{RESET}")
        print(f"  {'-' * (width - 4)}")
        print(f"  Name:    {name_str}")
        if "birthDate" in patient:
            print(f"  DOB:     {patient['birthDate']}")
        if "gender" in patient:
            print(f"  Gender:  {patient['gender']}")

    # Diagnoses with ICD-10 lookup
    conditions = clinical["conditions"]
    if conditions:
        print(f"\n{BOLD}  Diagnoses{RESET}")
        print(f"  {'-' * (width - 4)}")
        for cond in conditions:
            for coding in cond.get("code", {}).get("coding", []):
                code = coding.get("code", "?")
                icd_result = lookup_icd10_code(code)
                desc = icd_result["description"] if icd_result else coding.get("display", "Unknown")
                print(f"  {CYAN}{code}{RESET}  {desc}")

    # Claim details — procedures
    claim = clinical["claim_details"]
    if claim:
        items = claim.get("item", [])
        if items:
            print(f"\n{BOLD}  Requested Procedures{RESET}")
            print(f"  {'-' * (width - 4)}")
            for item in items:
                for coding in item.get("productOrService", {}).get("coding", []):
                    code = coding.get("code", "?")
                    display = coding.get("display", "")
                    print(f"  {CYAN}{code}{RESET}  {display}")

    # Provider
    practitioners = clinical["practitioners"]
    if practitioners:
        print(f"\n{BOLD}  Requesting Provider{RESET}")
        print(f"  {'-' * (width - 4)}")
        for prac in practitioners:
            name_parts = []
            for name in prac.get("name", []):
                prefix = " ".join(name.get("prefix", []))
                given = " ".join(name.get("given", []))
                family = name.get("family", "")
                name_parts.append(f"{prefix} {given} {family}".strip())
            name_str = ", ".join(name_parts) if name_parts else "Unknown"
            print(f"  Name:  {name_str}")
            for ident in prac.get("identifier", []):
                if ident.get("system", "").endswith("us-npi"):
                    print(f"  NPI:   {ident.get('value', '?')}")

    # Coverage
    coverage = clinical["coverage"]
    if coverage:
        print(f"\n{BOLD}  Insurance Coverage{RESET}")
        print(f"  {'-' * (width - 4)}")
        for cov in coverage:
            payor_names = []
            for payor in cov.get("payor", []):
                payor_names.append(payor.get("display", payor.get("reference", "?")))
            if payor_names:
                print(f"  Payor:  {', '.join(payor_names)}")
            if "subscriberId" in cov:
                print(f"  Member: {cov['subscriberId']}")

    # Supporting info
    supporting = clinical["supporting_info"]
    if supporting:
        print(f"\n{BOLD}  Supporting Clinical Narratives{RESET}")
        print(f"  {'-' * (width - 4)}")
        for info in supporting:
            wrapped = textwrap.fill(info, width=width - 4)
            for line in wrapped.split("\n"):
                print(f"  {line}")

    print(f"{'=' * width}\n")


def main() -> None:
    """CLI entry point for PA review demo."""
    parser = argparse.ArgumentParser(
        description="AI-driven prior authorization clinical review demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--case", type=str, help="Path to a single PA case JSON file")
    group.add_argument("--all", action="store_true", help="Review all 5 sample PA cases")
    group.add_argument("--inspect", type=str, help="Inspect a case's clinical data (no AI review)")
    args = parser.parse_args()

    if args.inspect:
        inspect_case(args.inspect)
    elif args.case:
        settings = ApplicationSettings()  # type: ignore[call-arg]
        asyncio.run(review_single_case(args.case, settings))
    elif args.all:
        settings = ApplicationSettings()  # type: ignore[call-arg]
        asyncio.run(review_all_cases(settings))


if __name__ == "__main__":
    main()
