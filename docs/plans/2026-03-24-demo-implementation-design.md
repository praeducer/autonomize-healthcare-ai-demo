# Demo Implementation Design
## AI-Driven Prior Authorization — Autonomize Healthcare AI Demo
### Date: 2026-03-24 | Status: Approved

## Summary

This design document captures the validated architecture and phased implementation plan for the AI-driven PA demo. The full implementation specification is at:
`C:\dev\solutions-architecture-agent\outputs\eng-2026-004-v2\plans\demo-implementation-prompt.md`

## Key Design Decisions

1. **Phased C→A progression**: Start cloud-agnostic (Anthropic SDK direct), end Azure-native. Each phase is independently demo-able.
2. **Real data over mocks**: Synthea FHIR R4 patients, Da Vinci PAS example structures, CDC ICD-10 codes, CMS Coverage DB via MCP.
3. **Standard FHIR models**: `fhir.resources.R4B` Pydantic v2 models, not custom-built.
4. **HAPI FHIR Server**: Real FHIR server (Docker) instead of mock Python service for clinical data.
5. **Jinja2 + HTMX + Pico CSS**: Single-container web dashboard, no npm/build step.
6. **Git version tagging**: v0.1.0 through v0.5.0 with release branches for safe fallback.
7. **5 realistic PA cases**: Real ICD-10/CPT codes, industry-standard clinical scenarios, designed for ex-Elevance Health audience.

## Research Sources Applied

- Anthropic Claude 4.x prompt engineering docs (2026)
- Spec-Driven Development (GitHub Spec Kit, Thoughtworks, Martin Fowler)
- AGENTS.md impact paper (arXiv 2601.20404) — 28.6% agent efficiency improvement
- Effective Context Engineering (Anthropic engineering blog, 2025)
- Da Vinci PAS Implementation Guide (HL7)
- CAQH Index 2024 (PA cost data)
- AMA 2024 PA Survey (physician burden data)

## Phase Summary

| Phase | Tag | What it proves | Fallback demo |
|---|---|---|---|
| 1: Core CLI Engine | v0.1.0 | AI determination works | Terminal |
| 2: REST API + FHIR | v0.2.0 | Integration patterns are real | Swagger UI |
| 3: Web Dashboard | v0.3.0 | Professional, demo-able product | Web browser |
| 4: Azure Deploy | v0.4.0 | Cloud-native capability | Live URL |
| 5: Managed Services | v0.5.0 | Enterprise architecture alignment | Azure-native |
