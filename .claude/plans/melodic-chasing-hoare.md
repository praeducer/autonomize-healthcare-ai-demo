# Presentation Overhaul — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Restructure the presentation to lead with the demo, fix diagram clarity issues, remove AWS content, and ensure perfect consistency across all presentation materials.

**Architecture:** Single-source-of-truth flow: `solution-architecture.md` → `presentation.md` → `speaker-script.md` → `slide-generation-prompts.md`. Changes propagate downstream.

---

## Context

Paul is presenting via Microsoft Teams screen share for an Autonomize AI Solutions Architect interview. The demo (Steps 1-3, v0.3.0) is working. The presentation needs restructuring based on Paul's feedback:
- Lead with the PA Request Lifecycle (the business process being automated)
- Open with demo right after the system design overview
- Remove AWS Equivalent content (only present final Azure decisions)
- Fix diagram clarity (actor vs role, generic component vs Azure service)
- Ensure cross-file consistency
- Don't discuss legacy integrations unless assignment-required
- Don't be overly strict about team compositions

**Interviewers:** Kris Nair (COO), Suresh Gopalakrishnan (SA), Ujjwal Rajbhandari (VP Engineering)

---

## Files to Modify

| File | Changes |
|------|---------|
| `docs/presentation/presentation.md` | Restructure slide order, remove AWS column, add demo slide, fix diagrams |
| `docs/presentation/speaker-script.md` | Align with new slide order, add demo context, update per-slide notes |
| `docs/presentation/slide-generation-prompts.md` | Align prompt numbers with new slide order |
| `docs/architecture/solution-architecture.md` | Minor fixes for consistency (FHIR team composition, legacy justification) |

## New Slide Order

| # | Slide | Was | Change |
|---|-------|-----|--------|
| 1 | Title & Introduction | Slide 1 | Keep |
| 2 | PA Request Lifecycle | Slide 5 | **Moved to front** — opens with the business process |
| 3 | Demo: Proof of Concept | NEW | High-level system diagram of demo + "this is a PoC" framing |
| 4 | **LIVE DEMO** | Was in speaker notes only | 5-minute CLI demo per `docs/presentation/demo-script.md` |
| 5 | System Context | Slide 3 | Fix: differentiate actor vs role in diagram |
| 6 | Component Architecture | Slide 4 | Fix: differentiate generic vs Azure. **Remove AWS column** |
| 7 | Why This Architecture | Slide 2 | Moved after diagrams — now answers "why these choices?" |
| 8 | Security Risks & Mitigations | Slide 6 | Keep |
| 9 | Progressive Delivery | Slide 9 | Keep (combines with demo context) |
| 10 | Discussion Starters | Slide 11 | Keep |

**Removed slides:** Clinical Data Integration (7), AI Model Monitoring (8), Scaling to 20 LOBs (10) — moved to appendix or speaker notes only. These are deep-dive topics for Q&A, not core presentation.

---

## Task 1: Restructure presentation.md

**Step 1:** Reorder slides per the new order above.

**Step 2:** Remove the AWS Equivalent table from Slide 6 (Component Architecture). Only show Azure services.

**Step 3:** Add new Slide 3: "Demo: Proof of Concept"
- Simple architecture diagram of what the demo actually implements:
  ```
  CLI / API / Dashboard → Clinical Review Engine → Claude (tool use)
                                                    ├── ICD-10 Lookup
                                                    ├── NPI Validation
                                                    ├── CMS Coverage
                                                    └── Clinical Data
  → ClinicalReviewResult → Audit Trail → FHIR ClaimResponse
  ```
- Frame as: "I built a working proof of concept to validate this architecture. It demonstrates the core clinical review flow — steps 4 and 5 of the lifecycle you just saw."
- Note limitations honestly: "Mock eligibility, local coverage criteria, synthetic data. Production would connect to Autonomize's PA Copilot on Genesis."

**Step 4:** Fix System Context diagram — use format `**Actor Name**\n_Role Description_` to differentiate the two text elements.

**Step 5:** Fix Component Architecture diagram — use format `**Generic Component**\nAzure: Service Name` with visual differentiation.

**Step 6:** Update "Why This Architecture" to be a justification slide that follows the diagrams, not leads them.

**Step 7:** Move Clinical Data Integration, AI Model Monitoring, and Scaling to 20 LOBs to an "Appendix" section at the bottom.

**Step 8:** Fix FHIR implementation wording — change "activity with clinical informaticists" to "discovery-phase activity with the implementation team" (broader).

**Step 9:** Remove or minimize legacy integration discussion — only mention it if directly referenced in the assignment.

**Step 10:** Commit.

---

## Task 2: Update speaker-script.md

**Step 1:** Reorder per-slide notes to match new slide order.

**Step 2:** Add demo transition notes between Slide 3 (PoC overview) and Slide 4 (live demo). Reference `docs/presentation/demo-script.md` for the full CLI walkthrough.

**Step 3:** Update opening thesis to mention the demo upfront: "...and I've built a working proof of concept to demonstrate the core review flow."

**Step 4:** Update the "Don't Elaborate" table — remove legacy topics, add demo-specific redirects.

**Step 5:** Update closing summary to reference the demo: "You saw the AI review 5 cases in real-time..."

**Step 6:** Commit.

---

## Task 3: Update slide-generation-prompts.md

**Step 1:** Renumber all prompts to match new slide order.

**Step 2:** Add prompt for new Slide 3 (Demo: Proof of Concept).

**Step 3:** Remove prompts for slides moved to appendix (unless kept as optional).

**Step 4:** Commit.

---

## Task 4: Cross-File Consistency Check

**Step 1:** Verify all claims, facts, and numbers match between:
- `solution-architecture.md` (source of truth)
- `presentation.md` (presentation view)
- `speaker-script.md` (delivery guide)
- `demo-script.md` (CLI walkthrough)

**Step 2:** Verify all Mermaid diagrams have correct arrow directions and clear labels.

**Step 3:** Run a mock interview simulation with stakeholder personas (Kris, Suresh, Ujjwal) — identify any content that would prompt questions Paul can't confidently answer based on `career-data.json`.

**Step 4:** Fix any consistency issues found.

**Step 5:** Commit all changes, push.

---

## Verification

| Check | How |
|-------|-----|
| Slide order matches plan | Read presentation.md |
| No AWS column in component architecture | Grep for "AWS Equivalent" |
| Demo slide exists (Slide 3) | Read presentation.md |
| Speaker script matches slide order | Compare section headers |
| All CAQH/AMA/CMS numbers consistent | Cross-reference sources table |
| No legacy integration emphasis | Grep for "legacy" |
| FHIR team composition is broad | Check wording |
| Demo script references match CLI output | Run `make review` and compare |

## Execution Batches

| Batch | Tasks |
|-------|-------|
| 1 | Task 1 (presentation restructure) — largest change |
| 2 | Tasks 2-3 (speaker script + prompts) — depend on Task 1 |
| 3 | Task 4 (consistency check + mock interview) |
