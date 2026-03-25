# AI-Driven Prior Authorization
## Documentation Hub | Paul Prae | www.paulprae.com

---

## How to Use These Files

| When | Open This | Purpose |
|------|-----------|---------|
| **First read** | [user-stories.md](user-stories.md) + [user-guide.md](user-guide.md) | Understand what the demo does and how to use each interface |
| **Morning demo build** | [Build step plans](../.claude/plans/) + [human-tasks.md](plans/human-tasks.md) | Claude Code plans + human checklist for each step |
| **After each build step** | [uat-guide.md](uat-guide.md) | Manual acceptance testing by user story |
| **Night before** | [interview-prep/study-guide.md](interview-prep/study-guide.md) | Azure mapping, diagram talking points, assumptions, key numbers |
| **1 hour before** | [interview-prep/pre-show-checklist.md](interview-prep/pre-show-checklist.md) | Statistics, rehearsal, demo prep, Teams screen share, risk awareness |
| **During presentation** | [presentation.md](presentation/presentation.md) + [speaker-script.md](presentation/speaker-script.md) | Slides on screen + speaking notes in hand |
| **During Q&A** | [interview-prep/quick-reference.md](interview-prep/quick-reference.md) | 18 anticipated questions with 60-second answers |
| **Before sending email** | [email-draft.md](interview-prep/email-draft.md) | Email to panel with attachments |

---

## File Index

### Presentation (`presentation/`)
| File | Description |
|------|-------------|
| [presentation.md](presentation/presentation.md) | 10-slide deck — standalone, GitHub-renderable, no speaker notes |
| [speaker-script.md](presentation/speaker-script.md) | Speaking notes, timing, coaching, pivot guides — references presentation slides |
| [demo-script.md](presentation/demo-script.md) | 5-minute CLI demo walkthrough for live presentation |
| [slide-generation-prompts.md](presentation/slide-generation-prompts.md) | All 10 prompts referencing presentation.md as source of truth |

### Demo (understand → use → test)
| File | Description |
|------|-------------|
| [user-stories.md](user-stories.md) | 9 user stories — who benefits, what they need, which interfaces and build steps |
| [user-guide.md](user-guide.md) | How to set up and use each interface (CLI, Claude Code, API, Dashboard) |
| [uat-guide.md](uat-guide.md) | Manual acceptance testing by user story — what to check and what "good" looks like |
| [human-tasks.md](plans/human-tasks.md) | Pre-interview checklist — infrastructure, automated tests, UAT, interview prep |

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

### Diagrams (7 views, 3 formats each — re-render with `make diagrams`)
| Diagram | .mmd | .svg | .png |
|---------|------|------|------|
| 01 System Context | [mmd](architecture/diagrams/01-system-context.mmd) | [svg](architecture/diagrams/01-system-context.svg) | [png](architecture/diagrams/01-system-context.png) |
| 02 Component Architecture | [mmd](architecture/diagrams/02-component-architecture.mmd) | [svg](architecture/diagrams/02-component-architecture.svg) | [png](architecture/diagrams/02-component-architecture.png) |
| 03 PA Request Flow | [mmd](architecture/diagrams/03-pa-request-flow.mmd) | [svg](architecture/diagrams/03-pa-request-flow.svg) | [png](architecture/diagrams/03-pa-request-flow.png) |
| 04 Clinical Data Access | [mmd](architecture/diagrams/04-clinical-data-access.mmd) | [svg](architecture/diagrams/04-clinical-data-access.svg) | [png](architecture/diagrams/04-clinical-data-access.png) |
| 05 Security & Zero Trust | [mmd](architecture/diagrams/05-security-zero-trust.mmd) | [svg](architecture/diagrams/05-security-zero-trust.svg) | [png](architecture/diagrams/05-security-zero-trust.png) |
| 06 LLMOps Pipeline | [mmd](architecture/diagrams/06-llmops-pipeline.mmd) | [svg](architecture/diagrams/06-llmops-pipeline.svg) | [png](architecture/diagrams/06-llmops-pipeline.png) |
| 07 Demo Architecture | [mmd](architecture/diagrams/07-demo-architecture.mmd) | [svg](architecture/diagrams/07-demo-architecture.svg) | [png](architecture/diagrams/07-demo-architecture.png) |

### Inputs
| File | Description |
|------|-------------|
| [assignment.md](inputs/assignment.md) | Interview assignment — AI-Driven Prior Authorization scenario |
| [stakeholder-profiles.md](inputs/stakeholder-profiles.md) | Panel profiles — Kris Nair, Suresh Gopalakrishnan, Ujjwal Rajbhandari |
| [job-description.md](inputs/job-description.md) | Solutions Architect job description — Autonomize AI |

### Plans
| File | Description |
|------|-------------|
| [Build step plans](../.claude/plans/) | Modular Claude Code plans: `shared-context.md` + `step-1` through `step-5` |
| [demo-implementation-design.md](plans/2026-03-24-demo-implementation-design.md) | Design summary for demo implementation |
