# Synthea FHIR Patient Data

Synthetic patient data from the [SMART on FHIR Synthea sample datasets](https://github.com/smart-on-fhir/sample-bulk-fhir-datasets).

## Download

```bash
make download-synthea
```

Or manually:

```bash
git clone --branch 10-patients --single-branch --depth 1 \
  https://github.com/smart-on-fhir/sample-bulk-fhir-datasets.git \
  data/synthea_fhir_patients/raw
```

## Contents

NDJSON files containing FHIR R4 resources (Patient, Condition, Observation, etc.) for 10 synthetic patients.

**Note:** Synthea does not generate Claim resources — PA claims are hand-curated in `data/sample_pa_cases/`.

## License

Apache 2.0 — see [source repository](https://github.com/smart-on-fhir/sample-bulk-fhir-datasets/blob/main/LICENSE).
