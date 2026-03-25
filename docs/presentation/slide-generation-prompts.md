# Slide Generation Prompts for Claude for PowerPoint

Each prompt below generates one slide. Use with the Claude for PowerPoint add-in.

**Workflow:**
1. Open [presentation.md](presentation.md) — this is the single source of truth for all slide content (9 slides + appendix)
2. For each slide, paste the corresponding prompt into Claude for PowerPoint
3. The prompt references `presentation.md` as context — attach it or paste the relevant slide section when prompted

**Tip:** If Claude for PowerPoint supports file attachment, attach `presentation.md` once at the start of your session and reference slide numbers in each prompt. This avoids repeating content.

---

## Slide 01: Title & Introduction
**Prompt:** "Create a title slide. Use the content from Slide 1 in the attached presentation.md. Title: 'AI-Driven Prior Authorization'. Subtitle: 'Solution Architecture for a Large US Health Plan'. Presenter: 'Paul Prae | Principal AI Engineer & Architect'. Website: 'www.paulprae.com'. Clean, professional layout."
**Diagram:** None

## Slide 02: PA Request Lifecycle
**Prompt:** "Create a slide titled 'PA Request Lifecycle' using Slide 2 from presentation.md. Insert ../architecture/diagrams/03-pa-request-flow.png as the main visual. Below it, include the 6-step summary line: Submit → Intake (OCR/extraction) → Validate (eligibility) → AI Review (coverage matching + confidence scoring) → Route (auto-approve / human review / pend) → Respond (payer core writeback + provider notification)."
**Diagram:** `../architecture/diagrams/03-pa-request-flow.png`

## Slide 03: Demo — Proof of Concept
**Prompt:** "Create a slide titled 'Demo — Proof of Concept' using Slide 3 content from presentation.md. Show the demo architecture diagram (CLI/API/Dashboard → Engine → Claude tools → Output). Below it, two columns: 'Demo scope' (4 bullets) and 'Production differences' (4 bullets). Include a callout: 'LIVE DEMO follows this slide'. Clean, professional layout."
**Diagram:** `../architecture/diagrams/demo-architecture.png`

## Slide 04: System Context
**Prompt:** "Create a slide titled 'System Context' using Slide 4 content from presentation.md. Insert the diagram image from ../architecture/diagrams/01-system-context.png on the left half. Place the 4-row actor/role/integration table on the right half."
**Diagram:** `../architecture/diagrams/01-system-context.png`

## Slide 05: Component Architecture
**Prompt:** "Create a slide titled 'Component Architecture' using Slide 5 from presentation.md. Insert ../architecture/diagrams/02-component-architecture.png as the main visual. Below or beside it, include the 8-row component/Azure service/purpose table."
**Diagram:** `../architecture/diagrams/02-component-architecture.png`

## Slide 06: Why This Architecture
**Prompt:** "Create a slide titled 'Why This Architecture' using Slide 6 content from presentation.md. Three sections: The Problem (manual PA costs, physician burden), The Opportunity (Altais metrics: 45%, 54%, 50%), Why These Specific Choices (4 bullet points). Bold the key numbers. Use the existing slide master."
**Diagram:** None

## Slide 07: Top 3 Security Risks & Mitigations
**Prompt:** "Create a slide titled 'Top 3 Security Risks & Mitigations' using Slide 7 from presentation.md. A 3-row table with columns: #, Risk (bold), Mitigation 1: Architectural, Mitigation 2: Operational. Include the 'Additional controls' line below the table. Insert ../architecture/diagrams/05-security-zero-trust.png if space allows."
**Diagram:** `../architecture/diagrams/05-security-zero-trust.png`

## Slide 08: Progressive Delivery
**Prompt:** "Create a slide titled 'Progressive Delivery' using Slide 8 from presentation.md. A 4-row table: Phase/Focus/Key Deliverable. Include the note about decision gates between phases."
**Diagram:** None

## Slide 09: Discussion Starters
**Prompt:** "Create a slide titled 'Discussion Starters' using Slide 9 from presentation.md. Three sections: Business Strategy (2 questions), Technical Depth (2 questions), Implementation (2 questions). Conversational, open layout."
**Diagram:** None

---

## Appendix Slides (Optional Generation)

The following slides were moved to the appendix. Generate only if time and context require them.

### Appendix A: Clinical Data Integration
**Prompt:** "Create an appendix slide titled 'Appendix A: Clinical Data Integration' using the Appendix A content from presentation.md. Include the source/protocol/auth table and the FHIR R4 role paragraph. Insert ../architecture/diagrams/04-clinical-data-access.png if space allows."
**Diagram:** `../architecture/diagrams/04-clinical-data-access.png`

### Appendix B: AI Model Monitoring & Feedback
**Prompt:** "Create an appendix slide titled 'Appendix B: AI Model Monitoring & Feedback' using the Appendix B content from presentation.md. Insert ../architecture/diagrams/06-llmops-pipeline.png. Two sections: 'Detect drift' (3 bullet points) and 'Feedback loop' (4 numbered steps)."
**Diagram:** `../architecture/diagrams/06-llmops-pipeline.png`

### Appendix C: Scaling to 20 LOBs
**Prompt:** "Create an appendix slide titled 'Appendix C: Scaling to 20 LOBs' using the Appendix C content from presentation.md. Comparison table: Multi-tenant vs Multi-instance across Cost/Isolation/Complexity. Include the recommendation callout and honest unknowns note."
**Diagram:** None
