# Simplify Architecture Pivot — Research & Recommendations

> **Date**: 2026-03-22
> **Author**: Claude Code (automated research)
> **Branch**: `claude/simplify-architecture-pivot-RAxvq`
> **Context**: Interview exercise for Autonomize AI — 2-day demo scope

---

## Executive Summary

The current architecture is **over-engineered for a 2-day demo**: Kafka (KRaft mode), PostgreSQL, AWS Bedrock, 6 implementation phases, 11 skeleton source files — none with real implementation. Meanwhile, Autonomize AI is **Azure-aligned** (Microsoft Pegasus program, Azure Marketplace, HIMSS 2026 in the Microsoft booth) and **already sells a PA Copilot**, meaning this demo risks competing with their own product.

This document presents three pivot options that simplify the architecture, align with Autonomize's actual strategic direction, and can be completed in the remaining time.

---

## Part 1: Research Findings

### 1.1 Current Codebase State

**Implementation status**: ~10% complete. All source files are skeleton/TODO.

| Category | Files | Status |
|----------|-------|--------|
| Infrastructure | docker-compose.yml, Makefile, pyproject.toml | Working |
| Documentation | CLAUDE.md, .claude/rules/*, README.md | Complete |
| Source code | 11 files in src/ | All skeleton/TODO |
| Tests | tests/test_e2e.py (6 tests) | All `pytest.skip()` |
| Mock services | 3 files in src/mock_services/ | All empty TODOs |

**What works**: Docker Compose brings up Kafka + PostgreSQL. Dependencies install. FastAPI starts but all endpoints raise `NotImplementedError`.

**Critical path items not started**: Pydantic models, DB schema, Kafka producers/consumers, mock services, PA processor, Bedrock integration, dashboard.

### 1.2 Autonomize AI — Company Intelligence

**Core product**: AI-powered healthcare automation platform.

**Key findings**:
- **Azure-aligned**: Listed on Azure Marketplace. Part of Microsoft Pegasus program. Showcasing at HIMSS 2026 from the Microsoft booth.
- **PA Copilot**: Their flagship product automates prior authorization with AI. Building another PA automation tool directly competes with their own product.
- **Agent Marketplace**: 100+ pre-built healthcare AI agents. This is their strategic growth direction — an ecosystem play, not a single-product play.
- **AI Studio**: Low-code/no-code platform for building and deploying healthcare AI agents. Integrates with their Agent Marketplace.
- **ServiceNow partnership**: Integrating AI agents into ServiceNow workflows for healthcare operations.
- **FHIR-native**: Their platform works with FHIR R4 data sources.
- **Multi-model**: Support multiple AI providers (not locked to one).

**Strategic direction**: Platform + marketplace, not point solutions. They want to be the "app store for healthcare AI agents."

### 1.3 Claude for Healthcare — Capabilities

**Native healthcare connectors** (available as agent skills / MCP tools):
- **CMS connector**: Medicare/Medicaid coverage policies, LCD/NCD databases
- **ICD-10 lookup**: Diagnosis code search and validation
- **NPI registry**: Provider verification
- **PubMed/clinical literature**: Evidence-based medicine search
- **FHIR R4 agent skill**: Native FHIR resource handling (Patient, Condition, Observation, Claim, Coverage)
- **Prior authorization agent skill**: End-to-end PA workflow automation

**Architecture pattern**: Model Context Protocol (MCP) — standardized tool interface for connecting LLMs to external data sources. This is the modern alternative to building custom API integrations.

**Tiered model routing**: Claude Haiku for triage/classification, Claude Sonnet for complex clinical reasoning, Claude Opus for audit/oversight. Cost optimization built into the architecture.

### 1.4 Strategic Misalignments in Current Plan

| Issue | Current Plan | Autonomize Reality |
|-------|-------------|-------------------|
| Cloud provider | AWS Bedrock | Azure-aligned (Marketplace, Pegasus, HIMSS booth) |
| Product overlap | Build PA automation | They already sell PA Copilot |
| Architecture style | Monolithic pipeline | Agent marketplace / modular agents |
| Complexity | Kafka + PostgreSQL + 6 phases | 2-day demo needs simplicity |
| Integration model | Custom API clients | MCP / agent skills pattern |

---

## Part 2: Pivot Recommendations

### Option A: "Agent Marketplace Contribution" (Recommended)

**Concept**: Build a modular healthcare AI agent that could plug into Autonomize's Agent Marketplace. Demonstrates understanding of their platform strategy without competing with PA Copilot.

**Why this wins the interview**:
- Shows you understand their *business*, not just the job description
- Demonstrates the agent pattern they're investing in
- Avoids the awkwardness of building a competitor to their flagship product
- Aligns with their Agent Marketplace (100+ agents) growth strategy

**Simplified architecture**:
```
FastAPI app (single process, no Kafka)
├── POST /agent/invoke — Run the agent on a clinical scenario
├── GET /agent/capabilities — Agent metadata (marketplace-compatible)
├── GET /agent/history/{session_id} — Audit trail
└── SQLite (file-based, no PostgreSQL needed)

Agent internals:
├── Claude API (direct, not Bedrock) — clinical reasoning
├── MCP tools — FHIR, ICD-10, NPI, CMS connectors
└── Pydantic models — structured I/O for marketplace compatibility
```

**Agent idea**: **Clinical Documentation Integrity (CDI) Agent** — Reviews clinical notes for documentation gaps, suggests more specific diagnosis codes, identifies query opportunities. This complements (not competes with) PA Copilot.

**Tech changes**:
- Drop Kafka → direct async processing
- Drop PostgreSQL → SQLite (or even in-memory dict for demo)
- Drop AWS Bedrock → direct Claude API (Anthropic SDK)
- Drop 6 phases → 3 phases (setup, agent logic, demo UI)
- Keep FastAPI, Pydantic v2, type hints, async

**Estimated scope**: ~500 lines of real code. Completable in 1 day.

---

### Option B: "PA Copilot Enhancement Layer"

**Concept**: Instead of rebuilding PA automation from scratch, build an *enhancement layer* that adds value on top of an existing PA system (like Autonomize's own PA Copilot). Position it as "here's how I'd extend your product."

**Simplified architecture**:
```
FastAPI app (single process)
├── POST /pa/enhance — Take a PA decision and add clinical evidence
├── POST /pa/appeal — Generate appeal letter from a denied PA
├── GET /pa/guidelines/{procedure_code} — Retrieve matching guidelines
└── SQLite for audit trail

Enhancement pipeline:
├── Claude API — clinical reasoning + letter generation
├── Mock PA Copilot API — simulates their existing product's output
└── CMS/clinical connectors — evidence gathering
```

**Why this works**: Shows you can add value to their existing product rather than replacing it. Appeal letter generation is a real pain point that PA Copilot may not fully address.

**Estimated scope**: ~400 lines. Completable in 1 day.

---

### Option C: "Simplified PA Demo (Current Direction, Descoped)"

**Concept**: Keep the current PA automation direction but aggressively simplify the architecture to actually complete it.

**Simplified architecture**:
```
FastAPI app (single process, no Kafka)
├── POST /pa/submit — Synchronous PA processing
├── GET /pa/status/{request_id} — Lookup from SQLite
├── GET /pa/dashboard — Simple metrics
└── SQLite for persistence

Processing pipeline (synchronous, in-process):
├── Mock eligibility check (in-memory)
├── Mock FHIR data (in-memory)
├── Mock guidelines (in-memory)
├── Claude API — determination
└── Store result in SQLite
```

**What to cut**:
- Kafka → synchronous processing (it's a demo)
- PostgreSQL → SQLite (zero config)
- AWS Bedrock → direct Claude API
- Separate mock service routers → inline mock functions
- Dashboard HTML → JSON-only metrics endpoint
- 6 phases → 2 phases (build it, test it)

**Risk**: Still builds a PA automation tool that competes with their product. But at least it will be *complete and working*.

**Estimated scope**: ~600 lines. Completable in 1.5 days.

---

## Part 3: Comparison Matrix

| Criteria | Option A (CDI Agent) | Option B (PA Enhancement) | Option C (Simplified PA) |
|----------|---------------------|--------------------------|------------------------|
| Strategic alignment | ★★★★★ | ★★★★☆ | ★★☆☆☆ |
| Avoids product overlap | ★★★★★ | ★★★★☆ | ★☆☆☆☆ |
| Technical impressiveness | ★★★★☆ | ★★★☆☆ | ★★★☆☆ |
| Completable in time | ★★★★★ | ★★★★★ | ★★★★☆ |
| Shows healthcare domain knowledge | ★★★★★ | ★★★★☆ | ★★★★☆ |
| Demonstrates agent/platform thinking | ★★★★★ | ★★★☆☆ | ★☆☆☆☆ |
| Uses existing codebase | ★★☆☆☆ | ★★★☆☆ | ★★★★★ |

**Recommendation**: **Option A** — it shows strategic thinking, aligns with their marketplace direction, avoids competing with PA Copilot, and is achievable in the remaining time.

---

## Part 4: Implementation Prompt

The following prompt can be given to Claude Code to implement whichever option is chosen. It is written for **Option A** (recommended) but includes notes for adapting to Options B or C.

---

### Claude Code Implementation Prompt

```markdown
# Task: Implement CDI (Clinical Documentation Integrity) Agent Demo

## Context
This is an interview exercise for Autonomize AI. We are pivoting from the
over-engineered PA automation architecture to a focused CDI Agent that
demonstrates understanding of Autonomize's Agent Marketplace strategy.

## What to Build

A FastAPI application that implements a Clinical Documentation Integrity agent.
The agent reviews clinical documentation (notes, diagnoses, procedures) and:
1. Identifies documentation gaps or insufficiently specific diagnosis codes
2. Suggests more specific ICD-10 codes based on clinical context
3. Generates physician query templates for missing documentation
4. Provides confidence scores and clinical rationale for each suggestion

## Architecture

Single-process FastAPI app. No Kafka. No PostgreSQL. SQLite for persistence.
Direct Claude API (Anthropic SDK) for clinical reasoning.

### Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/agent/invoke` | Submit clinical documentation for CDI review |
| GET | `/agent/capabilities` | Return agent metadata (marketplace-compatible format) |
| GET | `/agent/history/{session_id}` | Retrieve audit trail for a session |
| GET | `/health` | Health check |

### Data Models (Pydantic v2)

```python
class ClinicalDocument(BaseModel):
    """Input: clinical documentation to review."""
    patient_id: str
    encounter_date: date
    diagnosis_codes: list[str]  # Current ICD-10 codes
    procedure_codes: list[str]  # Current CPT codes
    clinical_notes: str  # Free-text clinical narrative
    provider_npi: str

class CDISuggestion(BaseModel):
    """A single CDI suggestion."""
    suggestion_type: Literal["code_specificity", "missing_documentation", "query_opportunity"]
    current_code: str | None
    suggested_code: str | None
    rationale: str
    confidence: float  # 0.0 - 1.0
    query_template: str | None  # Pre-written physician query

class CDIReviewResult(BaseModel):
    """Output: complete CDI review."""
    session_id: str  # UUID
    patient_id: str
    suggestions: list[CDISuggestion]
    overall_risk_score: float  # Documentation risk 0.0 - 1.0
    summary: str
    reviewed_at: datetime

class AgentCapabilities(BaseModel):
    """Marketplace-compatible agent metadata."""
    agent_id: str
    agent_name: str
    version: str
    description: str
    input_schema: dict
    output_schema: dict
    supported_standards: list[str]  # ["FHIR-R4", "ICD-10-CM", "CPT"]
    required_permissions: list[str]
```

### File Structure

```
src/
├── main.py              # FastAPI app, endpoints (reuse existing)
├── config.py            # Settings via env vars (reuse existing)
├── models.py            # Pydantic models above (reuse existing)
├── agent.py             # CDI agent logic (NEW - replaces pa_processor.py)
├── claude_client.py     # Claude API integration (replaces bedrock_client.py)
├── database.py          # SQLite operations (simplify existing)
├── mock_data.py         # Sample clinical documents (replaces mock_services/)
tests/
├── test_agent.py        # Agent unit tests
├── test_e2e.py          # End-to-end flow tests
```

### Implementation Rules

1. Python 3.12, type hints on everything, Pydantic v2 models for all I/O
2. Async FastAPI endpoints
3. Use `anthropic` SDK directly (not boto3/Bedrock)
4. SQLite via `aiosqlite` for async operations
5. All test data is synthetic — no real PHI
6. Every determination needs: rationale, confidence, audit trail
7. Structured output from Claude using tool_use or JSON mode
8. Include 5 sample clinical documents covering different scenarios:
   - Unspecified diabetes (E11.9 → suggest E11.65 with retinopathy)
   - Vague back pain (M54.5 → suggest M54.51 with radiculopathy)
   - Heart failure without stage (I50.9 → suggest I50.22 systolic chronic)
   - Sepsis without organism (A41.9 → suggest specific organism code)
   - Pneumonia unspecified (J18.9 → suggest J15.1 Pseudomonas)

### Claude Prompt Strategy

The agent should use a system prompt that establishes:
- Role: Clinical Documentation Integrity specialist
- Task: Review documentation against ICD-10-CM coding guidelines
- Output: Structured JSON matching CDISuggestion schema
- Constraints: Never fabricate clinical findings, only suggest based on documented evidence

### What NOT to Build
- No Kafka
- No PostgreSQL
- No AWS Bedrock
- No HTML dashboard (JSON API only)
- No Docker dependency for the app itself (Docker only for optional services)
- No multi-service architecture
- No FHIR server mock (use inline sample data)

### Success Criteria
1. `pip install -e ".[dev]"` works
2. `uvicorn src.main:app --reload` starts without errors
3. POST to `/agent/invoke` with sample clinical doc returns CDI suggestions
4. GET `/agent/capabilities` returns marketplace-compatible metadata
5. All tests pass with `pytest tests/ -v`
6. Demo takes < 2 minutes to set up and run
```

---

## Part 5: Adapting the Prompt for Options B or C

### For Option B (PA Enhancement Layer)

Replace the agent concept with:
- `POST /pa/enhance` — accepts a PA decision + clinical data, returns enriched evidence
- `POST /pa/appeal` — accepts a denied PA, generates appeal letter with citations
- `GET /pa/guidelines/{procedure_code}` — returns matching clinical guidelines
- Models: `PADecision`, `EnhancedEvidence`, `AppealLetter`, `GuidelineMatch`
- Mock a "PA Copilot response" as input (simulating their existing product)
- Claude prompt: "You are a clinical appeals specialist..."

### For Option C (Simplified PA)

Keep the current endpoint design but:
- Replace Kafka with synchronous in-process calls
- Replace PostgreSQL with SQLite
- Replace Bedrock with direct Claude API
- Inline all mock services as simple Python functions returning dicts
- Drop the dashboard HTML — JSON metrics only
- Models: Keep PARequest, PADetermination, AuditRecord as designed

---

## Appendix: Key URLs & References

- Autonomize AI: https://www.autonomize.ai/
- Autonomize Azure Marketplace: Azure Marketplace listing
- Autonomize Agent Marketplace: 100+ healthcare AI agents
- Autonomize PA Copilot: Flagship prior authorization product
- Claude Healthcare Connectors: CMS, ICD-10, NPI, PubMed via MCP
- FHIR R4 Spec: https://hl7.org/fhir/R4/
- ICD-10-CM: https://www.cms.gov/medicare/coding-billing/icd-10-codes
- Anthropic SDK: https://docs.anthropic.com/en/docs/sdks
