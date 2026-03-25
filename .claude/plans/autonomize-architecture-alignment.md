ultrathink: /plan

# Autonomize AI — Solution Architecture & Presentation Alignment Pass

## Objective

Perform a focused accuracy, terminology, and architecture-alignment pass across all docs in `docs/`. The goal is to earn hiring-panel trust by ensuring every claim, component name, integration point, data flow, and diagram precisely mirrors how Autonomize AI's platform is actually built and branded.

**Constraints**: Do NOT over-engineer or heavily refactor. Iterate existing work towards higher fidelity. Strictly enforce accuracy and Autonomize-native terminology. Keep it simple — this is an alignment pass, not a redesign.

## Current State

- **Demo**: Steps 1-3 complete (v0.3.0) — CLI, API, and web dashboard all working locally
- **LLM**: Claude Sonnet 4.6 (`claude-sonnet-4-6`) — latest Anthropic model family as of March 2026
- **Architecture doc**: `docs/architecture/solution-architecture.md` (v2.0, 2026-03-23) — SSOT for all deliverables
- **Diagrams**: 7 Mermaid files in `docs/architecture/diagrams/` rendered via local `mmdc` CLI
- **Presentation**: `docs/presentation/presentation.md` + PPTX/DOCX already generated

---

## Phase 1: Research (gather all external info BEFORE editing)

Execute these research tasks using the specified tools. Capture findings before touching any files.

### 1a. Autonomize First-Party Sources (WebFetch)

Fetch each URL and extract current terminology, metrics, and component names:

| # | URL | What to extract |
|---|-----|-----------------|
| 1 | `https://autonomize.ai/#platform` | Genesis platform description, sub-components, exact branding |
| 2 | `https://autonomize.ai/solutions` | Latest workflow descriptions, PA-specific metrics, customer outcomes |
| 3 | `https://autonomize.ai/news` | Any press releases newer than Oct 2025 that affect terminology or metrics |
| 4 | `https://www.businesswire.com/news/home/20251016579584/en/Autonomize-AI-Launches-Healthcare-Agents-Marketplace-and-AI-Studio-to-Let-Healthcare-Enterprises-Build-and-Govern-Their-Own-AI-Workflows` | AI Studio components, Agent Marketplace, Connectors & MCPs, exact quotes |
| 5 | `https://www.businesswire.com/news/home/20260224376992/en/Altais-Cuts-Prior-Authorization-Review-Time-by-45-and-Reduces-Manual-Errors-by-54-with-Autonomize-AI` | Altais PA metrics: 45% review time reduction, 54% error reduction, 50% auto-approval |
| 6 | `https://hitconsultant.net/2025/05/20/altais-and-autonomize-ai-partner-to-reduce-administrative-burden/` | "Compound AI" terminology, Genesis Platform reference |
| 7 | `https://azuremarketplace.microsoft.com/en-us/marketplace/apps/284109.autonomize-prior-auth-copilot` | Azure Marketplace listing — verify product name, description, capabilities |

### 1b. Autonomize PyPI Packages (WebFetch)

Fetch latest README for each package — these reveal internal architecture:

| Package | URL | Key details to extract |
|---------|-----|----------------------|
| `genesis-flow` | `https://pypi.org/project/genesis-flow/` | MLflow fork version, Azure Managed Identity, deployment model |
| `autonomize-model-sdk` | `https://pypi.org/project/autonomize-model-sdk/` | ModelHub SDK capabilities, KServe V2, inference types |
| `autonomize-observer` | `https://pypi.org/project/autonomize-observer/` | Logfire, Kafka topic name, Keycloak, AgentTracer |

### 1c. Azure Service Verification (Microsoft Learn MCP + WebSearch)

Use `microsoft_docs_search` and `microsoft_docs_fetch` MCP tools to verify these Azure services are current as of March 2026. Check for any renames, deprecations, or new features relevant to our architecture:

| Service in our docs | What to verify |
|--------------------|----------------|
| Azure AI Foundry | Confirm current name (was "Azure AI Studio" until late 2024). Verify Claude model availability via Foundry Models. |
| Azure AI Foundry Agent Service | Confirm GA status or preview timeline. Check MCP support, Python SDK. |
| Azure Health Data Services | Confirm FHIR R4 support, HIPAA/HITRUST certification |
| Azure AI Document Intelligence | Confirm current name, healthcare document processing features |
| Azure Container Apps | Confirm managed container features, auto-scale, serverless |
| Azure AI Search | Confirm hybrid vector + keyword search |
| Azure Service Bus Premium | Confirm HIPAA BAA eligibility |
| Microsoft Entra ID | Confirm SMART on FHIR support |

Also use `microsoft_code_sample_search` for any relevant Azure AI Foundry + Claude integration code samples that could strengthen the demo narrative.

### 1d. CMS/Regulatory Verification (WebFetch + CMS Coverage DB MCP)

| # | Action | Tool |
|---|--------|------|
| 1 | Verify CMS-0057-F Phase 1 (Jan 2026) and Phase 2 (Jan 2027) dates | WebFetch: `https://www.cms.gov/newsroom/fact-sheets/cms-interoperability-prior-authorization-final-rule-cms-0057-f` |
| 2 | Verify CAQH 2024 per-transaction costs ($10.97 provider, $3.52 payer) | WebFetch the CAQH Index report |
| 3 | Check for PA-related NCD updates relevant to our 5 test cases | `search_national_coverage` MCP tool |
| 4 | Validate ICD-10 codes used in our test cases are current 2026 codes | `lookup_code` and `validate_code` MCP tools for codes in `data/sample_pa_cases/` |

### 1e. Tech Stack Documentation (context7 MCP)

Use `resolve-library-id` then `query-docs` for current API/usage patterns:

| Library | Why |
|---------|-----|
| `anthropic` Python SDK | Verify tool use API, model ID format, latest features (March 2026) |
| `fastapi` | Verify async patterns, Jinja2 integration used in dashboard |
| `fhir.resources` | Verify R4B import paths, Pydantic v2 compatibility |

### 1f. Repo-Local File Review (Read tool)

Read these files to understand current state before editing:

**Input docs** (what the panel expects):
- `docs/inputs/assignment.md`
- `docs/inputs/job-description.md`
- `docs/inputs/stakeholder-profiles.md`

**Architecture** (SSOT):
- `docs/architecture/solution-architecture.md`
- `docs/architecture/research-context.md`
- `docs/architecture/requirements-traceability.md`
- All 7 `.mmd` diagram files in `docs/architecture/diagrams/`

**Presentation** (audience-facing):
- `docs/presentation/presentation.md`
- `docs/presentation/speaker-script.md`
- `docs/presentation/demo-script.md`

**Interview prep**:
- `docs/interview-prep/study-guide.md`
- `docs/interview-prep/quick-reference.md`
- `docs/interview-prep/email-draft.md`
- `docs/interview-prep/pre-show-checklist.md`

**Demo code** (verify demo-script.md claims match reality):
- `src/prior_auth_demo/clinical_review_engine.py`
- `src/prior_auth_demo/command_line_demo.py`
- `data/sample_pa_cases/README.md`

**Presenter background** (calibrate complexity level):
- `C:\dev\paulprae-com\data\generated\career-data.json`

---

## Phase 2: Verify Demo Alignment

Before updating docs, confirm the live demo matches what docs claim.

1. **Run `/invoke-pa-review-all`** skill — verify all 5 PA cases produce determinations. Note the actual output format, confidence scores, and determination types.
2. **Compare demo output to `demo-script.md`** — flag any discrepancies between what the demo actually outputs and what the script says.
3. **Check `healthcare_api_server.py` endpoints** — verify API routes match what `user-guide.md` documents.

---

## Phase 3: Edit — Architecture & Diagrams (highest impact first)

### 3a. `solution-architecture.md` — Master SSOT

This is the single source of truth. Apply all corrections here first, then cascade.

**Checks**:
1. Every component name traces to an authoritative source from Phase 1
2. Technology Decision Table uses current Azure service names (verified via Microsoft Learn MCP)
3. LLM references say "Claude Sonnet 4.6" with model ID `claude-sonnet-4-6` (latest Anthropic, March 2026)
4. All statistics have source citations (CAQH 2024 Index, Altais BusinessWire Feb 2026, AMA 2024 Survey)
5. No invented component names — if a name can't be traced to a source, remove it
6. Azure AI Foundry (not "Azure AI Studio") throughout — verify via Microsoft Learn
7. Microsoft Entra ID (not "Azure Active Directory" / "Azure AD")
8. Integration points match the assignment's three systems (Payer Core, Provider Portals/EDI, Clinical Data Sources)
9. Verified URLs in the Technology Decision Table still resolve and are correct

### 3b. Mermaid Diagrams (7 files)

For each `.mmd` file in `docs/architecture/diagrams/`, verify:
- Component names match `solution-architecture.md` exactly
- Data flow arrows match the integration descriptions
- No phantom components that aren't in the architecture doc
- Azure service names are current (verified in Phase 1c)

Files: `01-system-context.mmd` through `07-demo-architecture.mmd`

### 3c. `presentation.md` — Slide Deck SSOT

- Every claim traceable to `solution-architecture.md` or an authoritative source
- Architecture slide layering mirrors Genesis's actual stack
- Statistics match verified values from Phase 1
- Keep slides simple — avoid content that invites rabbit-hole questioning

### 3d. `speaker-script.md`

- Must reference `presentation.md` slides exactly (no added claims beyond slides)
- Calibrate to presenter's background — avoid deep MLflow/GenAI framework details
- Highlight Kafka familiarity, Azure expertise, healthcare data knowledge
- Include suggested deflection phrases for areas outside direct expertise

### 3e. `demo-script.md`

- Must match actual CLI/API output from Phase 2 verification
- Reference the 5 PA test cases by correct names/numbers
- Commands must work on Windows PowerShell (no `make` — use raw `python` commands)

---

## Phase 4: Cascade Updates

After the master doc and presentation are updated, cascade changes to:

| File | What to sync |
|------|-------------|
| `research-context.md` | Add any new source URLs from Phase 1; verify existing URLs resolve |
| `requirements-traceability.md` | Verify every assignment requirement maps to a slide |
| `study-guide.md` | Update terminology, anticipated questions, Azure service names |
| `quick-reference.md` | Update component names, metrics, key talking points |
| `email-draft.md` | Ensure correct deliverables and terminology |
| `pre-show-checklist.md` | Verify demo commands work on PowerShell |
| `user-guide.md` | Verify CLI commands, API endpoints match current code |

---

## Phase 5: Final QA

### 5a. Assignment Compliance Check

Re-read `docs/inputs/assignment.md` and verify every requirement is addressed:

| Assignment Section | Required Deliverable | Where Addressed |
|---|---|---|
| Part 1.1 | High-level architecture diagram (1-2 slides) | Verify slide # in `presentation.md` |
| Part 1.2 | Integration design for PA ingestion + Clinical data (2-3 slides) | Verify |
| Part 1.3 | Security & compliance top 3 risks (1-2 slides) | Verify |
| Part 2.1 | Executive summary (1 slide) | Verify |
| Part 2.2 | 12-week implementation roadmap (1-2 slides) | Verify |
| Part 3.1 | AI/ML strategy — drift detection, feedback loop (1-2 slides) | Verify |
| Part 3.2 | Future state scaling — multi-tenant vs multi-instance (1 slide) | Verify |

### 5b. Stakeholder Persona Review

Critically review all docs from each panelist's perspective:

**Kris Nair (COO)**: Does the presentation clearly communicate business value, ROI, and deployment speed? Are operational outcomes front and center?

**Suresh Gopalakrishnan (SA)**: Are integration points realistic? Does the FHIR data access pattern make sense? Are payer core system interfaces accurately described?

**Ujjwal Rajbhandari (VP Engineering)**: Are cloud architecture decisions justified? Is the LLMOps pipeline credible? Does the multi-tenant approach hold up to scrutiny?

Address any issues found during this review.

### 5c. Consistency Sweep

Final grep across all docs for:
- Outdated terms: "Azure AI Studio", "Azure Active Directory", "Azure AD", "Claude 3", "Claude Sonnet 3.5"
- Inconsistent component names between docs
- Statistics that appear in multiple docs with different values
- Broken internal cross-references

---

## Terminology Enforcement (apply everywhere)

| Correct Term | Wrong Variants to Fix |
|-------------|----------------------|
| Genesis | "Genesis AI Platform", "Genesis Platform" (unless quoting third-party) |
| Autonomize AI Studio | "AI Studio" alone as proper noun |
| Compound AI | generic "AI/ML" when describing Autonomize's approach |
| AI Agents | "AI models", "bots", "assistants" |
| Multi-agent Orchestration | "orchestration layer", "agent coordination" |
| Genesis-Flow | "MLflow" (when referring to Autonomize's fork) |
| ModelHub SDK | "model SDK", "model management" |
| Autonomize Observer | "observability SDK", "monitoring" |
| Curated Knowledge Hub | "knowledge base", "RAG system" |
| Connectors & MCPs | "integrations", "adapters" |
| Claude Sonnet 4.6 (`claude-sonnet-4-6`) | "Claude 3.5", "Claude Sonnet", outdated model IDs |
| Azure AI Foundry | "Azure AI Studio", "Azure OpenAI Service" |
| Microsoft Entra ID | "Azure Active Directory", "Azure AD" |

---

## Guardrails (presenter constraints)

- **Avoid multi-agent system deep dives** — keep orchestration high-level
- **Be cautious with MLflow/Genesis-Flow details** — presenter knows it at high level only
- **Kafka is familiar** — can discuss event streaming, but prefer managed services (Service Bus, Event Hubs)
- **Don't get more specific than the assignment requires** — high-level architecture, not detailed design
- **Keep diagrams lean** — only critical components from the assignment
- **Azure-first** — latest Azure services as of March 2026, no legacy naming
- **KISS/DRY/SSOT** — all docs form a cohesive whole, no contradictions
- **No traps** — don't create content that invites difficult rabbit-hole questioning
- **PowerShell** — demo commands must work on Windows (no `make`, no bash-only syntax)

---

## Quality Checklist (verify before completing)

- [ ] Zero invented terminology — every component name traces to an authoritative URL
- [ ] Zero unsupported statistics — every number has a source citation
- [ ] Consistent layering — same architecture stack in master doc, all diagrams, all slides, speaker script
- [ ] Demo script matches actual demo output (verified in Phase 2)
- [ ] Azure services use current names (verified via Microsoft Learn MCP)
- [ ] LLM references use Claude Sonnet 4.6 / `claude-sonnet-4-6`
- [ ] Cross-reference integrity — downstream docs consistent with `solution-architecture.md`
- [ ] `requirements-traceability.md` maps every assignment requirement to a slide
- [ ] Speaker script doesn't exceed presenter's comfort zone
- [ ] No dangling references to removed or renamed components
- [ ] Every assignment section (Parts 1-3) has corresponding slides
- [ ] All stakeholder personas addressed (COO, SA, VP Engineering)
- [ ] Demo commands work on Windows PowerShell

---

## Authoritative Sources of Truth

### 1. Autonomize Platform — Genesis (first-party)
- **Homepage platform section:** https://autonomize.ai/#platform
  - Genesis: "Purpose-built for healthcare, delivering safe, trusted AI systems to augment knowledge workflows."
  - Sub-components: AI Agents, Multi-agent Orchestration, Trust and Safety, Privacy and Security (HIPAA, SOC-II Type 2, AES-256, TLS 1.2+).

### 2. Autonomize AI Studio & Agent Marketplace (first-party press release)
- **BusinessWire Oct 16, 2025:** https://www.businesswire.com/news/home/20251016579584/en/Autonomize-AI-Launches-Healthcare-Agents-Marketplace-and-AI-Studio-to-Let-Healthcare-Enterprises-Build-and-Govern-Their-Own-AI-Workflows
  - Agent Marketplace (100+), Knowledge Hub (Curated Knowledge Graph), Low-Code Builder, Connectors & MCPs, Observability & Governance, Private Agent Marketplace.
  - CEO quote: "AI Studio turns agents into safe, composable teammates that encode policy and context."

### 3. Altais Partnership Results
- **BusinessWire Feb 24, 2026:** https://www.businesswire.com/news/home/20260224376992/en/Altais-Cuts-Prior-Authorization-Review-Time-by-45-and-Reduces-Manual-Errors-by-54-with-Autonomize-AI
  - 45% review time reduction, 54% error reduction, 50% auto-approval rate
- **HIT Consultant May 2025:** https://hitconsultant.net/2025/05/20/altais-and-autonomize-ai-partner-to-reduce-administrative-burden/
  - "Built on the Genesis Platform and powered by Compound AI"

### 4. Autonomize Python Packages (PyPI)
All published under https://pypi.org/org/AutonomizeAI/
- `genesis-flow` (v1.0.9) — MLflow v3.1.4 compatible fork, Azure Managed Identity, PostgreSQL
- `autonomize-model-sdk` (v1.1.73) — ModelHub SDK, KServe V2, Universal Inference Types
- `autonomize-observer` (v2.0.10) — Pydantic Logfire, Kafka (`genesis-traces-streaming`), Keycloak JWT

### 5. Azure Marketplace
- https://azuremarketplace.microsoft.com/en-us/marketplace/apps/284109.autonomize-prior-auth-copilot

### 6. Assignment & Stakeholder Inputs (repo-local)
- `docs/inputs/assignment.md` — interview assignment
- `docs/inputs/stakeholder-profiles.md` — Kris Nair (COO), Suresh Gopalakrishnan (SA), Ujjwal Rajbhandari (VP Engineering)
- `docs/inputs/job-description.md` — Solutions Architect role

---

## Output Format

For each file changed, report:
1. **What was wrong** — the specific misalignment or inaccuracy
2. **Correct info** — with source URL or verified reference
3. **Edit made** — brief description of the change

Execution order: `solution-architecture.md` → `presentation.md` → 7 diagrams → `speaker-script.md` → `demo-script.md` → cascade to remaining docs → final QA sweep.
