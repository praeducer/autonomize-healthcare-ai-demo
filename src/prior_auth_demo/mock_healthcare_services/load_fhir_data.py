"""Load Synthea FHIR NDJSON data into a HAPI FHIR server.

Reads all .ndjson files from data/synthea_fhir_patients/raw/,
parses each line as a FHIR resource, and POSTs it to the FHIR server.
Loads in dependency order to satisfy reference integrity.

Usage:
    python -m prior_auth_demo.mock_healthcare_services.load_fhir_data
"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path

import httpx

from prior_auth_demo.application_settings import ApplicationSettings

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "synthea_fhir_patients" / "raw"

# Load foundational resources first, then everything else
_PRIORITY_ORDER = ["Organization", "Location", "Practitioner", "PractitionerRole", "Patient"]
_SKIP_FILES = {"log.ndjson"}


async def load_ndjson_to_fhir(fhir_base_url: str) -> dict[str, int]:
    """Load all NDJSON files into the FHIR server. Returns counts per resource type."""
    counts: dict[str, int] = {}
    ndjson_files = sorted(_DATA_DIR.glob("*.ndjson"))

    if not ndjson_files:
        logger.error("No NDJSON files found in %s", _DATA_DIR)
        return counts

    # Sort files: priority resources first, then alphabetical
    def sort_key(path: Path) -> tuple[int, str]:
        name = path.stem.split(".")[0]
        if name in _PRIORITY_ORDER:
            return (0, _PRIORITY_ORDER.index(name))  # type: ignore[return-value]
        return (1, name)

    ndjson_files = sorted(ndjson_files, key=sort_key)

    async with httpx.AsyncClient(base_url=fhir_base_url, timeout=30.0) as client:
        for ndjson_path in ndjson_files:
            if ndjson_path.name in _SKIP_FILES:
                continue

            resource_type = ndjson_path.stem.split(".")[0]
            file_count = 0

            with ndjson_path.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    resource = json.loads(line)
                    resource_id = resource.get("id", "")

                    try:
                        response = await client.put(
                            f"/{resource_type}/{resource_id}",
                            json=resource,
                        )
                        if response.status_code in (200, 201):
                            file_count += 1
                        else:
                            logger.warning(
                                "Failed to load %s/%s: %s",
                                resource_type,
                                resource_id,
                                response.status_code,
                            )
                    except httpx.HTTPError as e:
                        logger.warning("HTTP error loading %s/%s: %s", resource_type, resource_id, e)

            counts[resource_type] = file_count
            print(f"  {resource_type}: {file_count} resources loaded")

    return counts


async def main() -> None:
    """Entry point for the FHIR data loader."""
    settings = ApplicationSettings()  # type: ignore[call-arg]
    fhir_url = settings.fhir_server_url

    print(f"Loading Synthea data into FHIR server at {fhir_url}...")
    print(f"Source: {_DATA_DIR}\n")

    counts = await load_ndjson_to_fhir(fhir_url)

    total = sum(counts.values())
    print(f"\nDone. {total} resources loaded across {len(counts)} types.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
