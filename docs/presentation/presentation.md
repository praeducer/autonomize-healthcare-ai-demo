# AI-Driven Prior Authorization — Solution Architecture
## Autonomize AI | Paul Prae | www.paulprae.com

> 9 slides + appendix | Priority-tiered for conversational format | Under 30 minutes
>
> **Tier A** (Must Present): Slides 1-3 + Live Demo | **Tier B** (Architecture): Slides 4-8 | **Tier C** (Appendix): Appendix slides

---

## Slide 1: Title & Introduction

# AI-Driven Prior Authorization
### Solution Architecture for a Large US Health Plan

**Paul Prae** | Principal AI Engineer & Architect
www.paulprae.com

---

## Slide 2: PA Request Lifecycle

```mermaid
flowchart LR
    subgraph "1. Submission"
        FAX["Fax / Scan"]
        PORTAL["Web Portal"]
        EDI["X12 278 EDI"]
    end

    subgraph "2. Intake"
        INGEST["Ingestion Gateway"]
        OCR["Document Processing<br/>OCR + Extraction"]
        NORM["Normalize to<br/>Canonical Format"]
    end

    subgraph "3. Validation"
        ELIG_CHK["Eligibility Check"]
        PA_REQ["PA Required?"]
    end

    subgraph "4. AI Review"
        CLIN_DATA["Retrieve Clinical Data"]
        AI_REVIEW["AI Clinical Review<br/>Coverage Matching"]
        CONF["Confidence Scoring"]
    end

    subgraph "5. Determination"
        AUTO["Auto-Approve<br/>High Confidence"]
        HUMAN["Human Review<br/>Low Confidence"]
        PEND["Pend for Info<br/>Missing Data"]
    end

    subgraph "6. Response"
        WRITE["Write to Payer Core"]
        NOTIFY["Notify Provider"]
    end

    FAX --> INGEST
    PORTAL --> INGEST
    EDI --> INGEST
    INGEST --> OCR
    OCR --> NORM
    NORM --> ELIG_CHK
    ELIG_CHK --> PA_REQ
    PA_REQ -->|"Yes"| CLIN_DATA
    PA_REQ -->|"No — Auto-approve"| WRITE
    CLIN_DATA --> AI_REVIEW
    AI_REVIEW --> CONF
    CONF -->|"Above Threshold"| AUTO
    CONF -->|"Below Threshold"| HUMAN
    CONF -->|"Insufficient Data"| PEND
    AUTO --> WRITE
    HUMAN --> WRITE
    PEND --> NOTIFY
    WRITE --> NOTIFY
```

**6-step process:** Submit → Intake (OCR/extraction) → Validate (eligibility) → AI Review (coverage matching + confidence scoring) → Route (auto-approve / human review / pend) → Respond (payer core writeback + provider notification)

---

## Slide 3: Demo — Proof of Concept

> "I built a working proof of concept to validate this architecture. It demonstrates the core clinical review flow — steps 4 and 5 of the lifecycle."

**What the demo implements:**

```mermaid
flowchart LR
    subgraph "Interfaces"
        CLI["CLI Terminal"]
        API["REST API<br/>Swagger UI"]
        DASH["Web Dashboard<br/>HTMX + Pico CSS"]
    end

    subgraph "Core Engine"
        ENGINE["Clinical Review Engine<br/>Python + Anthropic SDK"]
    end

    subgraph "Claude Tool Use"
        ICD["ICD-10 Lookup<br/>Local CDC Data"]
        NPI["NPI Validation<br/>Luhn-10 Check"]
        CMS["Coverage Criteria<br/>CMS LCD/NCD"]
        CLIN["Clinical Data<br/>FHIR R4 Bundle"]
    end

    subgraph "Output"
        RESULT["ClinicalReviewResult<br/>FHIR ClaimResponse"]
        AUDIT["Audit Trail<br/>SQLite"]
    end

    CLI --> ENGINE
    API --> ENGINE
    DASH --> ENGINE
    ENGINE --> ICD
    ENGINE --> NPI
    ENGINE --> CMS
    ENGINE --> CLIN
    ENGINE --> RESULT
    RESULT --> AUDIT
```

**Demo scope (Phase 0):**
- 5 realistic PA cases with real ICD-10/CPT codes
- AI reviews each case in ~30 seconds using Claude tool use
- FHIR R4 data models throughout (fhir.resources R4B)
- Three independent interfaces: CLI, REST API + Swagger, Web Dashboard

**Honest limitations:**
- Mock eligibility service (production: Payer Core System integration)
- Local coverage criteria (production: CMS Coverage Database API)
- Synthetic patient data (production: real clinical records via FHIR)
- Single-user demo (production: Azure Container Apps with auto-scaling)

> **[LIVE DEMO]** — See [demo-script.md](demo-script.md) for the 5-minute CLI walkthrough

---

## Slide 4: System Context

```mermaid
flowchart LR
    subgraph "Providers"
        PROV["**Healthcare Providers**<br/><i>Physicians, Facilities</i>"]
    end

    subgraph "Health Plan Systems"
        CORE["**Payer Core System**<br/><i>Enrollment, Benefits, Contracts</i>"]
        CLIN["**Clinical Data Sources**<br/><i>FHIR R4 + Legacy DB Connector</i>"]
    end

    subgraph "Autonomize AI Platform"
        PA_COPILOT["**PA Copilot**<br/><i>AI-Driven Review Engine</i>"]
    end

    subgraph "Regulatory"
        CMS["**CMS / State Regulators**<br/><i>Compliance Reporting</i>"]
    end

    PROV -->|"PA Requests<br/>Fax, Portal, X12 278"| PA_COPILOT
    CORE -->|"Eligibility + Benefits<br/>REST API"| PA_COPILOT
    CLIN -->|"Clinical Records<br/>FHIR R4 API"| PA_COPILOT
    PA_COPILOT -->|"Determinations<br/>REST API"| CORE
    PA_COPILOT -->|"Compliance Metrics<br/>CMS-0057-F"| CMS
    PA_COPILOT -->|"Status Updates<br/>Portal / Fax"| PROV
```

| Actor | Role | Integration |
|-------|------|-------------|
| Healthcare Providers | Submit PA requests via multiple channels | Fax, Portal, X12 278 |
| Autonomize AI Platform | AI-driven clinical review engine | PA Copilot on Genesis |
| Health Plan Systems | Eligibility, benefits, clinical data | REST API, FHIR R4 |
| Regulators (CMS) | Compliance reporting and oversight | CMS-0057-F metrics |

---

## Slide 5: Component Architecture

```mermaid
flowchart TB
    subgraph "Ingestion Layer"
        GW["**PA Ingestion Gateway**<br/><small>Azure API Mgmt + Functions</small>"]
        DOC["**Document Processing**<br/><small>Azure AI Document Intelligence</small>"]
    end

    subgraph "Integration Layer"
        ELIG["**Eligibility Service**<br/><small>Payer Core REST API</small>"]
        CLIN_AGG["**Clinical Data Aggregation**<br/><small>Azure Health Data Services</small>"]
        SB["**Message Queue**<br/><small>Azure Service Bus Premium</small>"]
    end

    subgraph "AI Engine"
        COPILOT["**Autonomize PA Copilot**<br/><small>Genesis Platform + Claude</small>"]
        ROUTER["**Determination Router**<br/><small>Confidence-Based Routing</small>"]
    end

    subgraph "Human Review"
        DASH["**Clinical Review Dashboard**<br/><small>Autonomize AI Studio</small>"]
    end

    subgraph "Response Layer"
        RESP["**Determination Response**<br/><small>Azure Functions</small>"]
        AUDIT["**Audit + Compliance**<br/><small>Immutable Blob Storage</small>"]
    end

    GW --> DOC
    GW --> SB
    DOC --> SB
    SB --> COPILOT
    ELIG --> COPILOT
    CLIN_AGG --> COPILOT
    COPILOT --> ROUTER
    ROUTER -->|"High Confidence"| RESP
    ROUTER -->|"Low Confidence"| DASH
    DASH --> RESP
    RESP --> AUDIT
```

| Component | Azure Service | Purpose |
|-----------|--------------|---------|
| Ingestion Gateway | API Management + Functions | Receives all PA channels |
| Document Processing | AI Document Intelligence | OCR for faxes |
| Eligibility Service | Payer Core REST API | Member validation |
| Clinical Data Aggregation | Health Data Services (FHIR R4) | Unified clinical context |
| PA Copilot | Genesis Platform + Claude | AI clinical review |
| Determination Router | Functions + Rules | Confidence-based routing |
| Clinical Review Dashboard | AI Studio | Human reviewer interface |
| Audit & Compliance | Immutable Blob Storage | Tamper-proof audit trail |

---

## Slide 6: Why This Architecture

**Now that you've seen the architecture and the demo**, here's why these specific choices matter.

**The Problem:** Manual PA processing costs **$10.97 in labor per provider transaction** ([CAQH 2024 Index, Prior Authorization row](https://www.caqh.org/hubfs/Index/2024%20Index%20Report/CAQH_IndexReport_2024_FINAL.pdf)), takes days, and burns out clinical staff — **93% of physicians** say PA delays patient care ([AMA 2024 Survey, p. 5](https://www.ama-assn.org/system/files/prior-authorization-survey.pdf)).

**The Opportunity — Altais + Autonomize AI** ([BusinessWire Feb 2026](https://www.businesswire.com/news/home/20260224376992/en/Altais-Cuts-Prior-Authorization-Review-Time-by-45-and-Reduces-Manual-Errors-by-54-with-Autonomize-AI)):
- **45%** reduction in PA review time
- **54%** reduction in manual errors
- **50%** auto-determination rate

**Why These Specific Choices:**
- AI-driven clinical review with human oversight — confidence thresholds route low-certainty cases to human reviewers, never auto-deny
- Configurable confidence thresholds — start conservative, tune with real data
- CMS-0057-F compliance readiness — FHIR R4 foundation meets Jan 2027 deadline
- Azure-native deployment — leverages Autonomize's Azure ecosystem

---

## Slide 7: Top 3 Security Risks & Mitigations

| # | Risk | Mitigation 1: Architectural | Mitigation 2: Operational |
| --- | ------ | ------------------------------ | --------------------------- |
| 1 | **PHI exposure through AI pipeline** | PHI tokenization before LLM — AI sees clinical facts without patient identity | Anthropic API usage ensures zero data retention for model training (per enterprise terms) |
| 2 | **Prompt injection via clinical documents** | Document sanitization + system prompt isolation | Output validation requiring evidence citations — hallucinated or injected claims fail verification |
| 3 | **Untraceable AI decisions** | Tamper-proof audit trail: model version, input hash, reasoning, evidence, confidence | Immutable 7-year retention with append-only writes |

**Additional controls:** Entra ID RBAC, AES-256 at rest, TLS 1.2+ in transit, private endpoints, no auto-deny without human review.

---

## Slide 8: Progressive Delivery

| Phase | Focus | Key Deliverable |
|-------|-------|-----------------|
| **Phase 0: Demo** | Prove the concept | Working AI PA review with mock data |
| **Phase 1: MVP** | Single LOB, single channel | Production PA processing with human review |
| **Phase 2: Scale** | Multi-channel, multi-LOB | Fax OCR, legacy data, LOB configuration |
| **Phase 3: Enterprise** | Full scale, compliance | All channels, 20 LOBs, CMS reporting |

Each phase produces a deployable, demonstrable system. Decision gates between phases use real performance data to scope the next phase.

---

## Slide 9: Discussion Starters

**Business Strategy:**
- How does the ServiceNow partnership change the payer integration strategy?
- What is the target auto-determination rate for Phase 1?

**Technical Depth:**
- How does the Genesis Platform handle coverage criteria updates?
- What's the Azure AI Foundry Agent Service integration status?

**Implementation:**
- Which LOB is the ideal Phase 1 candidate?
- What's been the biggest integration challenge with existing payer deployments?

---

## Appendix

### Appendix A: Clinical Data Integration

| Source | Protocol | Auth |
|--------|----------|------|
| Modern EMRs | FHIR R4 REST API | OAuth 2.0 / SMART on FHIR |
| Legacy DB Connector | DB connector / HL7 v2 | Service account + VNet |

**FHIR R4 role:** Interoperability standard for clinical data exchange. Modern sources expose it natively. Legacy data normalized to FHIR-compatible format before AI processing. Deep FHIR implementation is a discovery-phase activity with the implementation team.

**Security boundary:** All clinical data passes through PHI tokenization layer before reaching the AI engine.

### Appendix B: AI Model Monitoring & Feedback

**Detect drift:**
- Outcome monitoring — track overturn rate (human overrides AI), appeal rate, accuracy trends
- Automated evals — golden test cases benchmarked on schedule
- Confidence distribution — shifts signal model or data changes

**Feedback loop:**
1. Human reviewer corrections → updated eval dataset
2. Eval dataset → benchmark new model versions vs current
3. If improved → staged blue-green rollout
4. Guardrails always active: input filtering, output validation, clinical safety

### Appendix C: Scaling to 20 LOBs

| Approach | Cost | Isolation | Complexity |
|----------|------|-----------|------------|
| **Multi-tenant** | Lower | Logical | Lower |
| **Multi-instance** | Higher | Physical | Higher |

**Recommendation:** Start multi-tenant with per-LOB configuration. Autonomize Genesis Platform already supports it. Deploy separate instances only where regulation requires physical isolation.

**Honest unknowns:** The right answer depends on actual LOB rule complexity and regulatory requirements — both are discovery questions.

---

## Sources

| # | Claim | Source | Notes |
| --- | ----- | ------ | ----- |
| 1 | $10.97 manual PA labor cost (provider) | [2024 CAQH Index, p. 9](https://www.caqh.org/hubfs/Index/2024%20Index%20Report/CAQH_IndexReport_2024_FINAL.pdf) | Prior Authorization row; weighted avg labor cost (salaries + benefits + overhead) per manual transaction; excludes system costs |
| 2 | $3.52 manual PA labor cost (payer) | [2024 CAQH Index, p. 9](https://www.caqh.org/hubfs/Index/2024%20Index%20Report/CAQH_IndexReport_2024_FINAL.pdf) | Prior Authorization row; weighted avg labor cost per manual transaction, health plan side |
| 3 | ~$0.05 electronic PA cost (payer) | [2024 CAQH Index, p. 9](https://www.caqh.org/hubfs/Index/2024%20Index%20Report/CAQH_IndexReport_2024_FINAL.pdf) | Fully electronic transaction cost |
| 4 | 45% PA review time reduction | [Altais + Autonomize AI press release (Feb 2026)](https://www.businesswire.com/news/home/20260224376992/en/Altais-Cuts-Prior-Authorization-Review-Time-by-45-and-Reduces-Manual-Errors-by-54-with-Autonomize-AI) | Headline metric from joint press release |
| 5 | 54% manual error reduction | [Altais + Autonomize AI press release (Feb 2026)](https://www.businesswire.com/news/home/20260224376992/en/Altais-Cuts-Prior-Authorization-Review-Time-by-45-and-Reduces-Manual-Errors-by-54-with-Autonomize-AI) | Headline metric from joint press release |
| 6 | 50% auto-determination rate | [Altais + Autonomize AI press release (Feb 2026)](https://www.businesswire.com/news/home/20260224376992/en/Altais-Cuts-Prior-Authorization-Review-Time-by-45-and-Reduces-Manual-Errors-by-54-with-Autonomize-AI) | Headline metric from joint press release |
| 7 | 93% of physicians say PA delays care | [AMA 2024 Prior Authorization Survey, p. 5](https://www.ama-assn.org/system/files/prior-authorization-survey.pdf) | Survey of 1,000 practicing physicians, Dec 2024 |
| 8 | CMS-0057-F Phase 1 operational Jan 2026 | [CMS Interoperability & Prior Authorization Final Rule Fact Sheet](https://www.cms.gov/newsroom/fact-sheets/cms-interoperability-prior-authorization-final-rule-cms-0057-f) | Operational provisions: decision timeframes, metrics reporting |
| 9 | CMS-0057-F Phase 2 APIs due Jan 2027 | [CMS Interoperability & Prior Authorization Final Rule Fact Sheet](https://www.cms.gov/newsroom/fact-sheets/cms-interoperability-prior-authorization-final-rule-cms-0057-f) | API requirements: Patient Access, Provider Access, Payer-to-Payer, Prior Authorization APIs |
| 10 | Autonomize live at 3 of 5 largest US health plans | [Autonomize AI leadership hires press release (Feb 2026)](https://www.businesswire.com/news/home/20260226730170/en/Autonomize-AI-Strengthens-Leadership-with-Senior-Healthcare-Marketing-and-Regulatory-Hires) | Exact wording: "live at three of the five largest U.S. health plans" |
| 11 | Autonomize Prior Auth Copilot on Azure Marketplace | [Azure Marketplace listing](https://azuremarketplace.microsoft.com/en-us/marketplace/apps/284109.autonomize-prior-auth-copilot) | SaaS product listing |
| 12 | Autonomize + ServiceNow partnership | [Autonomize + ServiceNow press release (Mar 2026)](https://www.businesswire.com/news/home/20260305091710/en/Autonomize-AI-Partners-with-ServiceNow-to-Build-AI-Driven-Healthcare-Solutions-for-Payers) | AI-driven healthcare solutions for payers |
| 13 | Claude models available in Azure AI Foundry | [Microsoft Learn: Deploy Claude in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-claude) | Opus, Sonnet, Haiku model families via global standard deployment |
