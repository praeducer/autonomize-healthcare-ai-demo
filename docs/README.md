# AI-Driven Prior Authorization
## Documentation Hub | Paul Prae | www.paulprae.com

---

## How to Use These Files

| When | Open This | Purpose |
|------|-----------|---------|
| **Night before** | [interview-prep/study-guide.md](interview-prep/study-guide.md) | Azure mapping, diagram talking points, assumptions, key numbers |
| **1 hour before** | [interview-prep/pre-show-checklist.md](interview-prep/pre-show-checklist.md) | Checklists, risk awareness, rehearsal items |
| **During presentation** | [presentation.md](architecture/presentation.md) + [speaker-script.md](architecture/speaker-script.md) | Slides on screen + speaking notes in hand |
| **During Q&A** | [interview-prep/quick-reference.md](interview-prep/quick-reference.md) | 18 anticipated questions with 60-second answers |
| **Morning demo build** | [demo-implementation-prompt.md](../.claude/plans/demo-implementation-prompt.md) | Claude Code plan for building the PA review demo |
| **Before sending email** | [email-draft.md](interview-prep/email-draft.md) | Email to panel with attachments |

---

## File Index

### Presentation
| File | Description |
|------|-------------|
| [presentation.md](architecture/presentation.md) | 11-slide deck — standalone, GitHub-renderable, no speaker notes |
| [speaker-script.md](architecture/speaker-script.md) | Speaking notes, timing, coaching, pivot guides — references presentation slides |

### Interview Prep (3 files, organized by when you use them)
| File | When | Description |
|------|------|-------------|
| [study-guide.md](interview-prep/study-guide.md) | Night before | Azure↔AWS mapping, diagram talking points, 15 assumptions, key numbers |
| [pre-show-checklist.md](interview-prep/pre-show-checklist.md) | 1 hour before | Checklists (email, content, demo, diagrams), risk tables, sign-off |
| [quick-reference.md](interview-prep/quick-reference.md) | During Q&A | 18 panel questions with scripted answers, quick pivots table |

### Reference Documents
| File | Description |
|------|-------------|
| [solution-architecture.md](architecture/solution-architecture.md) | Master architecture reference — all other docs are views of this |
| [research-context.md](architecture/research-context.md) | Research findings with 50+ verified source URLs |
| [requirements-traceability.md](architecture/requirements-traceability.md) | Assignment → slide mapping (27 requirements, 100% coverage) |
| [email-draft.md](interview-prep/email-draft.md) | Interview email for panel |

### Slide Generation (for Claude for PowerPoint)
| File | Description |
|------|-------------|
| [slide-generation-prompts/README.md](slide-generation-prompts/README.md) | All 11 prompts referencing presentation.md as source of truth |

### Diagrams (6 progressive views, 3 formats each)
| Diagram | .mmd | .svg | .png |
|---------|------|------|------|
| 01 System Context | [mmd](architecture/diagrams/01-system-context.mmd) | [svg](architecture/diagrams/01-system-context.svg) | [png](architecture/diagrams/01-system-context.png) |
| 02 Component Architecture | [mmd](architecture/diagrams/02-component-architecture.mmd) | [svg](architecture/diagrams/02-component-architecture.svg) | [png](architecture/diagrams/02-component-architecture.png) |
| 03 PA Request Flow | [mmd](architecture/diagrams/03-pa-request-flow.mmd) | [svg](architecture/diagrams/03-pa-request-flow.svg) | [png](architecture/diagrams/03-pa-request-flow.png) |
| 04 Clinical Data Access | [mmd](architecture/diagrams/04-clinical-data-access.mmd) | [svg](architecture/diagrams/04-clinical-data-access.svg) | [png](architecture/diagrams/04-clinical-data-access.png) |
| 05 Security & Zero Trust | [mmd](architecture/diagrams/05-security-zero-trust.mmd) | [svg](architecture/diagrams/05-security-zero-trust.svg) | [png](architecture/diagrams/05-security-zero-trust.png) |
| 06 LLMOps Pipeline | [mmd](architecture/diagrams/06-llmops-pipeline.mmd) | [svg](architecture/diagrams/06-llmops-pipeline.svg) | [png](architecture/diagrams/06-llmops-pipeline.png) |

### Inputs
| File | Description |
|------|-------------|
| [assignment.md](inputs/assignment.md) | Interview assignment — AI-Driven Prior Authorization scenario |
| [stakeholder-profiles.md](inputs/stakeholder-profiles.md) | Panel profiles — Kris Nair, Suresh Gopalakrishnan, Ujjwal Rajbhandari |
| [job-description.md](inputs/job-description.md) | Solutions Architect job description — Autonomize AI |

### Plans
| File | Description |
|------|-------------|
| [demo-implementation-prompt.md](../.claude/plans/demo-implementation-prompt.md) | Claude Code plan for demo build (March 24 morning) |
| [execution-log.md](plans/execution-log.md) | Autonomous overnight execution log |
| [decisions.md](plans/decisions.md) | 3 technical decisions made overnight |
