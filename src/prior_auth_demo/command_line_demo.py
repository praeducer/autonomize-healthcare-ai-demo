"""CLI entry point for prior authorization review demo.

Usage:
    python -m prior_auth_demo.command_line_demo --case data/sample_pa_cases/01_lumbar_mri_clear_approval.json
    python -m prior_auth_demo.command_line_demo --all
"""

from __future__ import annotations

import argparse
import asyncio
import io
import json
import sys
from pathlib import Path

# Ensure stdout handles Unicode on Windows (Claude often uses symbols like >= in output)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from fhir.resources.R4B.bundle import Bundle

from prior_auth_demo.application_settings import ApplicationSettings
from prior_auth_demo.clinical_review_engine import ClinicalReviewResult, review_prior_auth_request

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

SAMPLE_CASES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "sample_pa_cases"


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


def print_result(result: ClinicalReviewResult, case_path: str) -> None:
    """Pretty-print a clinical review result to the terminal."""
    print(f"\n{'=' * 70}")
    print(f"{BOLD}Case:{RESET} {Path(case_path).name}")
    print(f"{BOLD}Determination:{RESET} {format_determination_badge(result.determination)}")
    print(f"{BOLD}Confidence:{RESET} {result.confidence_score:.0%}")
    print(f"{BOLD}Processing Time:{RESET} {result.review_duration_seconds:.1f}s")
    print(f"\n{BOLD}Clinical Rationale:{RESET}")
    print(f"  {result.clinical_rationale}")
    print(f"\n{BOLD}Guideline Citations:{RESET}")
    for citation in result.guideline_citations:
        print(f"  - {citation}")
    if result.missing_documentation:
        print(f"\n{BOLD}{YELLOW}Missing Documentation:{RESET}")
        for item in result.missing_documentation:
            print(f"  - {item}")
    print(f"{'=' * 70}\n")


async def review_single_case(case_path: str, settings: ApplicationSettings) -> ClinicalReviewResult:
    """Load and review a single PA case from a JSON file."""
    path = Path(case_path)
    if not path.exists():
        print(f"{RED}Error: File not found: {case_path}{RESET}", file=sys.stderr)
        sys.exit(1)

    with path.open() as f:
        data = json.load(f)

    bundle = Bundle.model_validate(data)
    result = await review_prior_auth_request(bundle, settings)
    print_result(result, case_path)
    return result


async def review_all_cases(settings: ApplicationSettings) -> list[ClinicalReviewResult]:
    """Review all PA cases in the sample_pa_cases directory."""
    case_files = sorted(SAMPLE_CASES_DIR.glob("*.json"))
    if not case_files:
        print(f"{RED}Error: No JSON files found in {SAMPLE_CASES_DIR}{RESET}", file=sys.stderr)
        sys.exit(1)

    print(f"\n{BOLD}{CYAN}Reviewing {len(case_files)} PA cases...{RESET}\n")
    results = []
    for case_file in case_files:
        result = await review_single_case(str(case_file), settings)
        results.append(result)

    # Print summary
    print(f"\n{BOLD}{'=' * 70}")
    print(f"SUMMARY: {len(results)} cases reviewed")
    print(f"{'=' * 70}{RESET}")
    for i, (case_file, result) in enumerate(zip(case_files, results)):
        print(
            f"  {i + 1}. {case_file.name}: "
            f"{format_determination_badge(result.determination)} "
            f"({result.confidence_score:.0%})"
        )
    print()
    return results


def main() -> None:
    """CLI entry point for PA review demo."""
    parser = argparse.ArgumentParser(
        description="AI-driven prior authorization clinical review demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--case",
        type=str,
        help="Path to a single PA case JSON file",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Review all 5 sample PA cases",
    )
    args = parser.parse_args()

    settings = ApplicationSettings()  # type: ignore[call-arg]

    if args.case:
        asyncio.run(review_single_case(args.case, settings))
    elif args.all:
        asyncio.run(review_all_cases(settings))


if __name__ == "__main__":
    main()
