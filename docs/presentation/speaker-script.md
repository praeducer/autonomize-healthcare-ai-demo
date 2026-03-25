# Speaker Script & Presentation Guide
## AI-Driven Prior Authorization | Autonomize AI Interview

> **Use alongside [presentation.md](presentation.md) during the interview.**
> For deeper technical reference, see [solution-architecture.md](../architecture/solution-architecture.md).

---

## Opening Thesis (60 seconds -- memorize this)

"I'm Paul Prae. I've spent 15 years building AI systems in healthcare -- most recently at Arine, where our platform served 50 million members across 45 health plans, and before that as an ML Solutions Architect at AWS.

I designed this architecture to answer a specific question: how does a large US health plan integrate Autonomize AI's PA Copilot safely and effectively? I've also built a working proof of concept to demonstrate the core review flow.

The answer is a 10-component Azure-native system that automates PA intake, clinical review, and determination -- with human oversight built in at every exception case. Based on Altais's February 2026 results: 45% faster reviews, 54% fewer errors, 50% auto-determination rate.

I'll take you through the architecture in tiers -- executive context, then technical depth, then implementation path. Stop me anywhere."

---

## Time Navigation

| Time Remaining | Action |
|---|---|
| 30+ min | Slides 1-4, live demo (5 min), slides 5-9, discussion |
| 20-25 min | Slides 1-4, live demo (3 cases only), slides 7-8, discussion |
| 15-20 min | Slides 1-4, abbreviated demo (1 case), key architecture points |
| Under 15 min | Opening thesis + 1 demo case. Offer to go deeper. |

**3-minute rule**: If you've been on one slide for 3 minutes without a question, stop and ask "Is this the right level of detail?"

---

## Per-Slide Notes

### Slide 1: Title & Introduction
**Core (30 sec)**: "15 years healthcare AI. Arine 50M members. AWS ML SA. Excited about PA automation."
**Don't elaborate**: Resist going deep on any single past role. 60 seconds max on intro.
**Pivot**: If asked about specific experience -- "Let me walk through the architecture -- I'll connect each decision to experience as we go."

### Slide 2: The Problem & Opportunity
**Core (30 sec)**: "Manual PA is expensive and slow. Altais proved Autonomize cuts review time 45%, errors 54%. My architecture integrates that with safety controls."
**Key point**: This sets up the business case before showing any technical detail.
**For Kris**: Lead with business outcomes -- the three Altais metrics are on this slide.

### Slide 3: PA Request Lifecycle
**Core (30 sec)**: "Six-step process, standard PA workflow per AMA and CAQH. The innovation is in steps 4 and 5 -- AI-driven clinical review with confidence-based routing."
**Key point**: This is the business process we're automating. Everything in this architecture serves this flow.
**For Kris**: This connects directly to the 45% review time reduction Altais achieved.

### Slide 4: Demo -- Proof of Concept
**Core (30 sec)**: "I built this to validate the architecture. Same clinical review engine, FHIR R4 data models, real ICD-10 and CMS coverage criteria. Three interfaces -- CLI, API with Swagger, and a web dashboard."
**Transition to demo**: "Let me show you it working." Then follow [demo-script.md](demo-script.md) for the 5-minute CLI walkthrough.
**After demo**: "What you just saw is Phase 0 of the roadmap. The same engine would integrate with your PA Copilot on Genesis."

### Slide 5: System Context
**Core (30 sec)**: "Four actors, one AI platform in the middle. Providers submit through existing channels. Determinations flow back to payer core."
**Expanded**: Generic-first design. Integration points labeled. No new workflows for providers.
**For Suresh**: "These are the standard patterns I've seen at scale."

### Slide 6: Solution Architecture
**Core (30 sec)**: "Ten components with Azure labels. AI engine is Autonomize's PA Copilot -- I'm integrating it, not rebuilding it."
**Expanded**: Azure Service Bus for async (simpler than Kafka, HIPAA-covered on Premium). Every service has AWS equivalent.
**For Ujjwal**: "Azure because Autonomize is Azure-native. My AWS background translates directly -- patterns identical, service names change."
**Don't elaborate**: Don't list all 10 components. Let the diagram speak.

### Slide 7: Why This Architecture
**Core (30 sec)**: "Five specific choices, each with a business benefit. Safety-first routing, configurable thresholds, CMS compliance, Azure-native, full audit trail."
**Expanded**: Each architectural choice maps to a business outcome -- safety, adaptability, compliance, ecosystem fit, regulatory retention.
**For Kris**: This answers "why these specific choices?" -- lead with business benefits.
**Don't elaborate**: Don't dive into CAQH methodology or CMS rule details. If asked: "CAQH measures labor costs -- salaries, benefits, overhead -- per transaction via annual industry survey."

### Slide 8: Security Risks & Mitigations
**Core (30 sec)**: "Three risks, three architectural mitigations. AI-specific controls first -- that's the novel attack surface."
**Risk 1**: PHI tokenization -- LLM sees clinical facts without patient identity.
**Risk 2**: Prompt injection defense -- output validation requires evidence citations. Injected content can't produce evidence-backed determination.
**Risk 3**: Tamper-proof audit trail -- model version, input hash, reasoning, evidence, confidence. 7-year retention.
**For Ujjwal**: "This is zero trust for AI -- verify every input, validate every output, log everything."

### Slide 9: Progressive Delivery
**Core (30 sec)**: "Four phases, each producing something real. AI features front-loaded."
**Don't elaborate**: No specific week numbers or team sizes. If asked: "Depends on discovery findings and team composition."

### Slide 10: Discussion Starters
**Core**: "These are questions I'd ask in real discovery. Love to explore any of these with you."

---

## Conversation Pivot Phrases

**Anchor on slide**: "Let me point you to slide [N] -- I've captured that there."
**Buy time**: "Great question -- are you asking about [A] or [B]?"
**Redirect from gap**: "That's exactly what I'd discover in a real engagement. Here's what I'd ask and why it matters..."
**Back to business value**: "The Altais result is the evidence. My architecture delivers the same pattern."
**Invite the panel**: "Where would you like to spend time? I'm comfortable going deep on integration or stepping back to business case."

---

## Closing Summary (30 seconds -- land this no matter what)

"You've seen the architecture and the demo -- a system where Autonomize's PA Copilot integrates safely into the health plan's ecosystem. Reliable intake, AI-driven clinical review with human oversight, full audit trail. The proof of concept validates the core flow. Phase 1 puts it in production. I'm excited about this problem space."

---

## "Don't Elaborate" Topics

| Topic | Brief Redirect |
|---|---|
| FHIR Da Vinci IG | "Discovery-phase activity with the implementation team -- beyond this architecture's scope" |
| NIST control IDs | "I design to principles; control ID mapping follows the architecture" |
| EDI X12 segments | "Handled by gateway -- translator-tool territory" |
| KS test / PSI | "LLMOps is behavioral -- overturn rates and eval regression" |
| Snowflake / dbt | "Not in scope -- PA processing is transactional, not analytical" |
| InterQual vs MCG | "Clinical governance decision -- the AI matches whatever the client uses" |
| TriZetto Facets API | "Discovery question -- designed around assumed REST interface" |
| Demo internals | "Happy to walk through the code -- it's on GitHub" |
| Why not LangChain | "Direct Anthropic SDK -- simpler, more control, no framework abstraction" |

---

## Handling "I Don't Know"

**Template**: "That's a great discovery question -- here's what I'd want to find out and why it matters for the architecture."

**Example**: "Do you know the Payer Core API spec?" -- "I don't -- that's the first thing I'd validate. If REST, the synchronous eligibility check works as designed. If SOAP or batch-only, I'd redesign to use a pre-fetched cache. I've built both patterns."

---

## Live Demo Walkthrough (5-6 minutes)

> Use during the presentation after Slide 4 (Demo slide), before the architecture deep-dive (Slides 5-9). Run all 5 cases in order 1->4->3->5->2.

**Opening** (30 seconds):
"To validate the architecture I'm proposing, I built a working proof-of-concept this morning. It demonstrates the core AI-driven PA review flow -- the same pattern that would integrate with Autonomize's PA Copilot in production."

**Case 1 -- Lumbar MRI Auto-Approval** (60 seconds):
"Here's a straightforward case -- lumbar MRI after 8 weeks of failed conservative treatment. The AI checks the ICD-10 codes against CMS coverage criteria, validates the provider's NPI, reviews the clinical evidence, and returns an approval with 90%+ confidence in under 30 seconds. In production, this type of case would be auto-approved without human review -- that's the 50% auto-determination rate Altais achieved with your platform."

**Case 4 -- Humira Missing Documentation** (60 seconds):
"Now a specialty drug case -- Humira for rheumatoid arthritis. The provider says 'failed methotrexate' but didn't include the dose, duration, or labs. Instead of a generic 'send more info' response, the AI identifies the five specific items missing -- methotrexate details, RF and CRP labs, DAS28 score, biosimilar consideration, and complete DMARD history. This reduces back-and-forth cycles, which is the number one provider complaint about PA."

**Case 3 -- Spinal Fusion Complex Review** (90 seconds):
"This is the most interesting case -- a 2-level spinal fusion. The AI finds that some criteria are met -- MRI confirms stenosis, EMG confirms radiculopathy -- but flags specific gaps: only 8 PT sessions versus the 12 typically required, no epidural steroid injections attempted, and the patient's A1C of 8.2% creates surgical risk. Rather than approve or deny, it routes to the medical director with a structured summary for a peer-to-peer call. This is where AI augments the clinical reviewer instead of replacing them."

**Case 5 -- Urgent Oncology** (60 seconds):
"An urgent case -- first-line Keytruda for Stage IIIA non-small cell lung cancer. The AI recognizes the NCCN Category 1 recommendation for PD-L1-high NSCLC, confirms the clinical evidence, and approves within the 72-hour urgent timeline mandated by CMS-0057-F. The audit trail captures the full reasoning chain, model version, and evidence citations -- that's your 7-year HIPAA compliance trail."

**Case 2 -- Cosmetic Rhinoplasty Denial** (30 seconds):
"Finally, a clear denial -- rhinoplasty with a mismatched diagnosis code. The AI catches the mismatch between actinic keratosis and rhinoplasty, identifies the lack of functional indication, and generates a denial with the specific clinical reason required by CMS-0057-F. In Phase 1 production, this would still route to a human reviewer before finalizing the denial."

**Bridge to Architecture** (60 seconds):
"What you just saw is Phase 0 of the roadmap. The clinical review engine uses Claude's tool use to check NPI registries, validate ICD-10 codes, and look up CMS coverage criteria -- real data sources, not hardcoded rules. The FHIR R4 data model means this plugs directly into your existing health plan integrations. Phase 1 would connect this to Autonomize's PA Copilot on the Genesis Platform, replace the mock eligibility service with a real Facets integration, and add the clinical review dashboard you already have in AI Studio."

---

## Appendix Notes

> These notes cover appendix slides. Do not present proactively -- use only if asked or if significant time remains.

### Appendix A: Clinical Data Integration
**Core (30 sec)**: "Two worlds -- FHIR R4 and legacy. Aggregation service presents unified context. FHIR at label level."
**Don't elaborate**: No Da Vinci IG, no SMART on FHIR scopes, no FHIR resource schemas. If asked: "Discovery-phase activity with the implementation team."

### Appendix B: AI Model Monitoring & Feedback
**Core (30 sec)**: "LLMOps not MLOps. Monitoring LLM output quality -- evals, guardrails, human feedback."
**Key distinction**: Drift = coverage criteria changed, not model weights shifted. Overturn rate is the key metric.
**For Ujjwal**: "Traditional ML drift metrics (KS, PSI) apply if we add a triage classifier. LLM monitoring is eval-driven."

### Appendix C: Scaling to 20 LOBs
**Core (30 sec)**: "Multi-tenant with per-LOB config as starting point. Separate instances only for regulatory isolation."
**Key framing**: Trade-off discussion, not prescriptive answer. Discovery questions determine the right approach.
