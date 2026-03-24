# AI Tooling Configuration

How Claude Code is configured for this project, what plugins and MCP tools are installed, and how to set up a new contributor's machine.

Last updated: March 24, 2026

---

## Overview

This project uses [Claude Code](https://code.claude.com) (Anthropic's AI coding assistant CLI) as the primary development tool. The configuration is optimized for healthcare AI development with FHIR R4, prior authorization workflows, and progressive build steps from CLI to Azure cloud.

### Configuration Files (Committed)

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Project context, tech stack, build commands — loaded automatically |
| `.claude/rules/architecture.md` | Architecture constraints and service boundaries |
| `.claude/rules/coding-standards.md` | Python coding standards, naming, error handling |
| `.claude/rules/healthcare-standards.md` | FHIR R4, ICD-10, Da Vinci PAS, audit trail rules |
| `.claude/settings.json` | Shared project settings: enabled plugins, MCP servers, permissions, hooks |
| `.claude/plans/` | Build step implementation plans (shared-context + step-1 through step-5) |
| `.mcp.json` | MCP server definitions (healthcare APIs, Docker) |
| `.env.example` | Environment variable template |

### Configuration Files (Personal / Gitignored)

| File | Purpose |
|------|---------|
| `.claude/settings.local.json` | Personal overrides (gitignored) |
| `.env` | API keys and secrets (gitignored) |
| `~/.claude/settings.json` | User-global Claude Code settings |

---

## Installed Plugins

### Healthcare Domain (from `anthropics/healthcare` marketplace)

| Plugin | What It Does |
|--------|-------------|
| **`fhir-developer@healthcare`** | FHIR R4 development expertise. Provides reference docs for resource structures, required fields, value sets (status codes, gender, intent), coding systems (LOINC, SNOMED CT, RxNorm, ICD-10), OperationOutcome error handling, Bundle transactions, pagination, and SMART on FHIR authorization. |
| **`prior-auth-review@healthcare`** | Prior authorization workflow automation. Two-subskill workflow: (1) Intake & Assessment — validates data, extracts clinical info, assesses medical necessity; (2) Decision & Notification — generates auth decision with provider notification. Includes decision policy rubric and notification letter templates. Requires CMS, NPI, and ICD-10 MCP servers. |

### Development Workflow (from `claude-plugins-official` marketplace)

| Plugin | What It Does |
|--------|-------------|
| **`context7`** | Live library documentation via MCP. Fetches current, version-specific docs for any library on demand. Add `use context7` to prompts. 14 of 15 project libraries are indexed (see Context7 section below). |
| **`hookify`** | Natural-language hook creation. Use `/hookify` to create behavioral guardrails without editing JSON. |
| **`feature-dev`** | Guided feature development with codebase analysis and architecture focus. |
| **`frontend-design`** | Polished, presentation-grade frontend interfaces. Used for Build Step 3 dashboard (Jinja2 + HTMX + Pico CSS). |
| **`superpowers`** | 14 workflow skills: brainstorming, writing-plans, executing-plans, TDD, systematic-debugging, verification-before-completion, subagent-driven-development, dispatching-parallel-agents, requesting-code-review, finishing-a-development-branch, and more. |
| **`code-review`** | Code review for pull requests. |
| **`pr-review-toolkit`** | Comprehensive PR review using specialized agents. |
| **`commit-commands`** | Git commit and push-PR workflows via `/commit` and `/commit-push-pr`. |
| **`code-simplifier`** | Auto-suggested after writing code. Simplifies for clarity and maintainability. |
| **`security-guidance`** | Security best practices. Important for healthcare: PHI protection, audit trail integrity, SQL injection prevention. |
| **`claude-md-management`** | CLAUDE.md file maintenance and optimization. |
| **`claude-code-setup`** | Setup optimization and automation recommendations. |

---

## MCP Servers

Defined in `.mcp.json` and enabled in `.claude/settings.json`.

### Healthcare APIs (HTTP, from deepsense.ai)

| Server | URL | Tools | Project Usage |
|--------|-----|-------|---------------|
| **`cms-coverage-db`** | `https://mcp.deepsense.ai/cms_coverage/mcp` | `cms_search_all`, `cms_search_ncds`, `cms_search_lcds`, `cms_lcd_details`, `cms_search_articles`, `cms_article_details`, `cms_search_medcac`, `cms_contractors`, `cms_states`, `cms_whats_new` | Clinical review engine checks Medicare coverage criteria (NCDs/LCDs) for requested procedures. |
| **`npi-registry`** | `https://mcp.deepsense.ai/npi_registry/mcp` | NPI lookup, provider validation | Clinical review engine validates requesting provider's NPI, retrieves specialty and practice info. |
| **`icd10-codes`** | `https://mcp.deepsense.ai/icd10_codes/mcp` | ICD-10-CM/PCS code validation and lookup | Clinical review engine validates diagnosis codes. Supplements the local CDC reference file (`data/reference/icd10cm_codes_2026.tsv`). |

### Development Tools (stdio)

| Server | Command | Project Usage |
|--------|---------|---------------|
| **`docker-mcp`** | `uvx mcp-server-docker` | Container management for HAPI FHIR server (Build Step 2+), app containerization (Build Step 4). |

### Plugin MCP (auto-managed)

| Server | Project Usage |
|--------|---------------|
| **`context7`** (via plugin) | Live library documentation. Connected automatically when `context7@claude-plugins-official` is enabled. |

---

## Context7 Library Coverage

Verified March 24, 2026. All project dependencies are indexed except `fhir.resources` (covered by `fhir-developer@healthcare` instead).

| Library | Context7 ID | Snippets |
|---------|-------------|----------|
| Anthropic Python SDK | `/anthropics/anthropic-sdk-python` | 127 |
| FastAPI | `/fastapi/fastapi` | 1,679 |
| Pydantic | `/pydantic/pydantic` | 680 |
| pydantic-settings | `/pydantic/pydantic-settings` | 206 |
| httpx | `/encode/httpx` | 245 |
| HTMX | `/bigskysoftware/htmx` | 1,747 |
| Pico CSS | `/picocss/pico` + `/websites/picocss` | 377 |
| Jinja2 | `/pallets/jinja` | 193 |
| uvicorn | `/kludex/uvicorn` | 150 |
| pytest | `/pytest-dev/pytest` | 771 |
| pytest-asyncio | `/pytest-dev/pytest-asyncio` | 104 |
| aiosqlite | `/omnilib/aiosqlite` | 33 |
| polyfactory | `/litestar-org/polyfactory` | 140 |
| ruff | `/astral-sh/ruff` | 7,045 |
| FHIR R4 (HL7 spec) | `/hl7/fhir` | 5,412 |
| fhir.resources (Python) | *Not indexed* | Use `fhir-developer@healthcare` |

**Usage**: Add `use context7 for /fastapi/fastapi` (or any ID above) to prompts for live docs.

---

## Automation Hooks

Defined in `.claude/settings.json` and active for all contributors.

| Hook | Trigger | Effect |
|------|---------|--------|
| **Ruff auto-format** | PostToolUse on Write or Edit of `.py` files | Runs `ruff format` + `ruff check --fix` automatically after every Python file change. |

---

## Build Step Workflow

Each build step follows this standard workflow (detailed in `.claude/plans/shared-context.md`):

1. `/brainstorming` — understand requirements
2. `/feature-dev` — structured implementation plan
3. `use context7` — fetch live library docs
4. `/tdd` — write tests before implementation
5. `fhir-developer` / `prior-auth-review` skills — healthcare domain guidance
6. MCP tools (CMS, NPI, ICD-10) — real healthcare data in the engine
7. Ruff auto-formats on save (hook)
8. `/simplify` — code quality pass
9. `make lint && make test` — automated verification
10. `/code-review` — pre-commit review
11. `/commit` — git tag, release branch

---

## New Contributor Setup

### Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| **Node.js** | 18+ | [nodejs.org](https://nodejs.org/) |
| **Python** | 3.12+ | [python.org](https://www.python.org/downloads/) |
| **Docker** | Latest | [docker.com](https://www.docker.com/products/docker-desktop/) |
| **Git** | Latest | [git-scm.com](https://git-scm.com/) |
| **GitHub CLI** | Latest | [cli.github.com](https://cli.github.com/) |
| **uv** (optional) | Latest | `pip install uv` — needed for `docker-mcp` server (`uvx` command) |

### Step 1: Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code@latest
claude --version  # Should print 2.1.81+
```

### Step 2: Authenticate

```bash
claude auth login
# Follow the browser-based OAuth flow
# OR set ANTHROPIC_API_KEY environment variable
```

### Step 3: Clone and Install

```bash
git clone https://github.com/<org>/autonomize-healthcare-ai-demo.git
cd autonomize-healthcare-ai-demo
pip install -e ".[dev]"
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY
```

### Step 4: Add the Healthcare Marketplace

```bash
claude plugins marketplace add anthropics/healthcare
```

### Step 5: Install Required Plugins

```bash
# Healthcare domain
claude plugins install fhir-developer@healthcare
claude plugins install prior-auth-review@healthcare

# Development workflow (from official marketplace)
claude plugins install context7@claude-plugins-official
claude plugins install hookify@claude-plugins-official
claude plugins install feature-dev@claude-plugins-official
claude plugins install frontend-design@claude-plugins-official
claude plugins install superpowers@claude-plugins-official
claude plugins install code-review@claude-plugins-official
claude plugins install pr-review-toolkit@claude-plugins-official
claude plugins install commit-commands@claude-plugins-official
claude plugins install code-simplifier@claude-plugins-official
claude plugins install security-guidance@claude-plugins-official
claude plugins install claude-md-management@claude-plugins-official
claude plugins install claude-code-setup@claude-plugins-official
```

### Step 6: Configure Global Settings

Add to `~/.claude/settings.json` (or merge with existing):

```json
{
  "permissions": {
    "allow": [
      "Bash(*)",
      "Read",
      "Edit",
      "Write",
      "Glob",
      "Grep",
      "WebSearch",
      "WebFetch",
      "Agent",
      "TodoWrite",
      "Skill",
      "NotebookEdit"
    ]
  },
  "effortLevel": "high"
}
```

### Step 7: Verify Setup

```bash
cd autonomize-healthcare-ai-demo

# Check plugins
claude plugins list  # Should show 14 enabled plugins

# Check MCP servers (start a session to verify)
claude mcp list  # Should show context7 connected + 4 project servers

# Run tests
make install
make lint
make test
```

### Step 8: Start Working

```bash
cd autonomize-healthcare-ai-demo
claude
# The session loads CLAUDE.md, rules, settings, MCP servers, and plugins automatically.
# Build step plans are in .claude/plans/ — reference them with:
#   "Execute .claude/plans/step-1-core-engine.md"
```

---

## Troubleshooting

### MCP servers not connecting

Project MCP servers (cms-coverage-db, npi-registry, icd10-codes, docker-mcp) only load when Claude Code starts from the project directory. Verify with `claude mcp list` from within the repo root.

### Context7 not finding a library

Use the exact Context7 ID from the table above. Example: `use context7 for /fastapi/fastapi` (not just "fastapi").

### Ruff hook not running

The hook is defined in `.claude/settings.json`. Verify JSON is valid: `python -m json.tool .claude/settings.json`. If the hook was modified during the session, open `/hooks` to reload.

### Healthcare plugins not showing

Run `claude plugins marketplace add anthropics/healthcare` to add the marketplace, then install the plugins.

### Settings not taking effect

Settings load in order: `~/.claude/settings.json` (global) → `.claude/settings.json` (project) → `.claude/settings.local.json` (personal). Later files override earlier ones. Restart Claude Code after changes.

### Cloud settings sync

Claude Code settings are file-based and not synced to Anthropic's cloud. To share settings across machines, commit `.claude/settings.json` (project-scoped) and document global settings in this file. Personal settings (`settings.local.json`, `~/.claude/settings.json`) must be configured per machine.
