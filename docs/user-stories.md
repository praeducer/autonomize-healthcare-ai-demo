# User Stories

> **SSOT for**: What user stories exist, who they serve, and which interfaces/steps they apply to.

Canonical reference for all demo user stories. Each story maps to one or more interfaces and is verified via UAT.

**Related documents:**

- How to test each story: [`docs/uat-guide.md`](uat-guide.md)
- How to use each interface: [`docs/user-guide.md`](user-guide.md)
- Pre-interview checklist: [`docs/plans/human-tasks.md`](plans/human-tasks.md)

## Stories

| ID | As a... | I want to... | So that... | Interfaces | Step |
|----|---------|-------------|-----------|------------|------|
| US-1 | Clinical reviewer | Submit a PA case and receive an AI determination | I can make faster, evidence-based decisions | CLI, Claude Code, API, Dashboard | 1+ |
| US-2 | Clinical reviewer | See evidence-backed reasoning with guideline citations | I can trust and audit the AI's recommendation | CLI, Claude Code, API, Dashboard | 1+ |
| US-3 | Medical director | Know that ambiguous cases route to human review | No borderline case is auto-approved without oversight | CLI, Claude Code, API, Dashboard | 1+ |
| US-4 | Compliance officer | See specific clinical reasons for every denial | We meet CMS-0057-F audit requirements | CLI, Claude Code, API, Dashboard | 1+ |
| US-5 | Provider | See exactly what documentation is missing when a case is pended | I can resubmit with the right information quickly | CLI, Claude Code, API, Dashboard | 1+ |
| US-6 | Operations | Access PA review via REST API with Swagger docs | We can integrate the engine with other systems | API | 2+ |
| US-7 | Compliance officer | Have every determination in an immutable audit trail | We have a tamper-proof record for regulators | API | 2+ |
| US-8 | Clinical reviewer | Use a web dashboard to submit and review cases | I have a visual, intuitive interface for demos and daily work | Dashboard | 3+ |
| US-9 | Presenter | Demo the system readable during Teams screen share | The interview audience can read everything clearly | Dashboard | 3+ |
