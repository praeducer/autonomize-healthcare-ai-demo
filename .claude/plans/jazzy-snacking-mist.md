# Autonomize Architecture Alignment Pass — Execution Plan

## Context

Interview for Autonomize AI Solutions Architect role is **this afternoon (2026-03-25)**. Steps 1-3 of the demo are complete (v0.3.0). All docs exist and are well-structured. This is an **alignment pass** — verify accuracy, fix terminology, ensure consistency, and simplify where needed.

**Key constraints:**
- **presentation.md is unlocked** — other agent finished (added solution architecture diagram slide)
- **email-draft.md is frozen** — already sent, keep as archive
- **Models**: Claude Opus 4.6 (`claude-opus-4-6`) + Sonnet 4.6 (`claude-sonnet-4-6`)
- **Demo vs Enterprise**: Phase 0 demo ≠ Phases 1-3 enterprise. Never conflate.
- **No new complexity**: Don't add content Paul can't explain in 60 seconds
- **No unverified claims**: Every fact traces to an authoritative source
- **Protect the demo**: Verify it works before and after changes
- **Plenty of time**: Focus on quality, accuracy, completeness

---

## Step 0: Safety — Tag Current State

```
git tag pre-alignment-pass
```

---

## Known Issues

1. `study-guide.md:66` — "Azure Active Directory" → "Microsoft Entra ID"
2. `pre-show-checklist.md:65` — "All 6 diagrams" → "All 7 diagrams"
3. `requirements-traceability.md` — All items stuck at "PLANNED" status
4. Model references need audit — ensure Opus 4.6 and Sonnet 4.6 used correctly throughout

---

## Phase 1: Research (parallel subagents, read-only)

### Group A: Autonomize Platform Verification (WebFetch)
- Fetch 7 Autonomize first-party URLs — verify they resolve, extract current terminology/metrics
- Fetch 3 PyPI packages (genesis-flow, autonomize-model-sdk, autonomize-observer)

### Group B: Azure & Tech Stack (Microsoft Learn MCP + context7)
- Verify Azure service names current (AI Foundry, Health Data Services, Entra ID, etc.)
- Verify Anthropic SDK, FastAPI, fhir.resources patterns

### Group C: Regulatory & Clinical (WebFetch + MCP tools)
- Verify CMS-0057-F dates + CAQH costs
- Validate ICD-10 codes in our 5 test cases

### Group D: Demo Verification
- Run `/invoke-pa-review-all` — capture actual output for demo-script alignment

**No commits — research only.**

---

## Phase 2: Quick Fixes

| Task | File | Change |
|------|------|--------|
| **2a** | `docs/interview-prep/study-guide.md:66` | "Azure Active Directory" → "Microsoft Entra ID" |
| **2b** | `docs/interview-prep/pre-show-checklist.md:65` | "All 6 diagrams" → "All 7 diagrams" |
| **2c** | All docs | Audit Claude model references → Opus 4.6 / Sonnet 4.6 |
| **2d** | All docs | Fix any other outdated terms found in Phase 1 |

**COMMIT 1**: `fix: correct terminology — Entra ID, diagram count, model versions`

---

## Phase 3: Architecture SSOT Updates

| Task | File | Change |
|------|------|--------|
| **3a** | `solution-architecture.md` | Apply Phase 1 corrections. Ensure demo (Phase 0) clearly separated from enterprise (Phases 1-3). Verify all stats have citations. Bump to v2.1. |
| **3b** | `requirements-traceability.md` | Update PLANNED → ADDRESSED for Steps 1-3 items |
| **3c** | `research-context.md` | Add new sources from Phase 1, update unverified claims |
| **3d** | `diagrams/*.mmd` (7 files) | Verify component names match SSOT. Fix if mismatched. |

**COMMIT 2**: `docs: update architecture SSOT — version bump, traceability, research context`

---

## Phase 4: Presentation Improvements

This is the highest-value editorial work. Slide-by-slide assessment from Paul:

### Slides that are GOOD (light touch only):
- **Slide 4: Demo — Proof of Concept** — no changes needed
- **Slide 6b: Solution Architecture — Components** — no changes needed
- **Appendix B: AI Model Monitoring & Feedback** — no changes needed
- **Sources** — no changes needed

### Slides that need SIMPLIFICATION:

**4a. Slide 5: System Context — SIMPLIFY**
- Current `01-system-context.mmd` is hard for Paul to follow and explain
- Simplify the diagram: reduce node count, clearer labels, remove edge-label noise
- Goal: Paul can walk through 4 actors and their relationships in 30 seconds

**4b. Slide 6a: Solution Architecture Diagram — CAREFUL EDITS**
- Expect significant Autonomize platform terminology updates from Phase 1 research
- Don't over-complicate — keep component count manageable
- Ensure Autonomize-native terms (Genesis, PA Copilot, AI Studio, etc.)

**4c. Slide 9: Progressive Delivery — ALIGN TO AGILE SDLC**
- Current version is just a 4-row table (Phase 0-3)
- Align to standard Agile/iterative delivery lifecycle
- Briefly summarize what process executes in each phase (sprint-based, iterative)
- Keep it simple — a sentence per phase describing the Agile approach

**4d. Slide 10: Discussion Starters — SIMPLIFY**
- Make questions easier for Paul to remember and use naturally
- Remove any questions that could lead to rabbit holes Paul can't navigate
- Keep questions that demonstrate genuine curiosity about Autonomize's platform

**4e. Appendix C: Scaling — SIMPLIFY**
- Current content is good but could be more concise
- Keep the multi-tenant vs multi-instance table
- Simplify the recommendation text

### Other presentation files:

**4f. `speaker-script.md`** — Verify metrics match SSOT, deflection phrases appropriate
**4g. `demo-script.md`** — Verify against Phase 1g demo output, PowerShell commands work
**4h. `quick-reference.md`** — Verify Q&A accuracy with updated content
**4i. `study-guide.md`** — Full pass after Phase 2 fixes
**4j. `pre-show-checklist.md`** — Verify checklist reflects current state
**4k. `user-guide.md`** — Verify CLI/API commands match code

**COMMIT 3**: `docs: simplify system context, improve progressive delivery, clean discussion starters`
**COMMIT 4**: `docs: align interview prep docs with architecture SSOT`

---

## Phase 5: Final QA

### 5a: Consistency Sweep
- Grep for outdated terms across all docs (zero tolerance)
- Grep for metric consistency (Altais, CAQH, CMS dates)
- Verify no doc conflates demo with enterprise

### 5b: Assignment Compliance
- Re-read `docs/inputs/assignment.md`
- Verify every Part 1-3 requirement → slide in requirements-traceability.md

### 5c: Demo Verification (final)
- Run `/invoke-pa-review-all` one more time
- Verify demo-script.md commands work on PowerShell

### 5d: Diagram Re-render (only if .mmd files changed)
- Re-render with `make diagrams`
- Regenerate PPTX with `python scripts/generate_deck.py`

**COMMIT 5**: `docs: final QA — re-render diagrams, regenerate deck` (if needed)

---

## Risk Mitigations

| Risk | Mitigation |
|------|-----------|
| **Demo breaks** | Tag `pre-alignment-pass` first. Only edit docs, not code. Run demo before AND after. |
| **New content Paul can't explain** | Every change must pass: "Can Paul walk through this in 60 seconds?" |
| **Unverified claims** | Phase 1 verifies everything. Unverifiable claims get flagged or removed. |
| **Demo/enterprise confusion** | Explicit Phase 0 vs Phases 1-3 labeling in every relevant doc. |

## Files Modified (in order)

1. `docs/interview-prep/study-guide.md` — terminology fix + full review
2. `docs/interview-prep/pre-show-checklist.md` — diagram count + checklist review
3. `docs/architecture/solution-architecture.md` — SSOT corrections, version bump
4. `docs/architecture/requirements-traceability.md` — status updates
5. `docs/architecture/research-context.md` — source verification
6. `docs/architecture/diagrams/01-system-context.mmd` — SIMPLIFY
7. `docs/architecture/diagrams/*.mmd` — consistency check (6 more files)
8. `docs/presentation/presentation.md` — slides 5, 6a, 9, 10, Appendix C improvements
9. `docs/presentation/speaker-script.md` — metrics alignment
10. `docs/presentation/demo-script.md` — demo output alignment
11. `docs/interview-prep/quick-reference.md` — Q&A accuracy
12. `docs/user-guide.md` — command verification

## Verification

- `/invoke-pa-review-all` produces correct determinations (before and after)
- Grep for outdated terms returns zero results
- All metrics consistent across all docs
- Demo commands work on PowerShell
- Every assignment requirement traces to a slide
- Paul can explain each slide in 60 seconds
