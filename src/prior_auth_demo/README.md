# Prior Authorization Demo — Python Code Guide

> **How to use this guide:** Open this README side-by-side with each Python file as you reach its section. Each section tells you which file to open. The guide follows the same path a PA request takes through the system — from configuration, through the CLI or API entry point, into the AI engine, and out to the audit store and dashboard.
>
> **Target audience:** Paul Prae — experienced AI architect and engineer returning to hands-on Python after several years. You know the concepts; this refreshes the syntax and shows you exactly how this codebase applies them so you can confidently extend it in a live coding session.
>
> **Companion doc:** [study-guide.md](../../docs/interview-prep/study-guide.md) covers architecture, Azure services, and interview strategy. This README covers the Python code.

---

## Table of Contents

1. [Python 3.12+ Refresher](#1-python-312-refresher)
2. [Project Structure & Packaging](#2-project-structure--packaging)
3. [Configuration Layer](#3-configuration-layer)
4. [CLI Entry Point — Following a PA Request](#4-cli-entry-point--following-a-pa-request)
5. [The AI Engine — Core Business Logic](#5-the-ai-engine--core-business-logic)
6. [FastAPI REST API — HTTP Entry Point](#6-fastapi-rest-api--http-entry-point)
7. [Audit Store — Async SQLite](#7-audit-store--async-sqlite)
8. [Mock Healthcare Services](#8-mock-healthcare-services)
9. [Web Dashboard — Server-Side Rendering](#9-web-dashboard--server-side-rendering)
10. [Testing Patterns](#10-testing-patterns)
11. [Live Coding Cheat Sheet](#11-live-coding-cheat-sheet)

---

## 1. Python 3.12+ Refresher

> **No file to open.** This section is a standalone syntax reference. Skim it now, return to it before the interview.

### Type Hints (used on every function in this codebase)

```python
# Basic types
def greet(name: str) -> str:
    return f"Hello, {name}"

# Optional / Union (modern syntax — Python 3.10+)
def find(id: str) -> dict[str, Any] | None:   # replaces Optional[dict[str, Any]]
    ...

# Collections (built-in generics — Python 3.9+, no need to import List/Dict)
def process(items: list[str]) -> dict[str, int]:
    ...

# Literal types (restricts values to a fixed set)
from typing import Literal
status: Literal["APPROVED", "DENIED", "PENDED_FOR_REVIEW"]
```

**Why it matters for this role:** The job description calls for "designing and integrating APIs." Type hints are how this codebase documents every function contract — and Pydantic enforces them at runtime.

### Pydantic v2 Models (the backbone of this app)

```python
from pydantic import BaseModel, Field

class ReviewResult(BaseModel):
    """Pydantic validates types on construction — not just documentation."""
    determination: str
    confidence: float = Field(ge=0.0, le=1.0)  # constrained range
    citations: list[str] = []                    # default empty list

# Construction validates automatically
result = ReviewResult(determination="APPROVED", confidence=0.92)
result.confidence = 1.5  # would raise ValidationError

# Serialization
result.model_dump()           # → dict
result.model_dump_json()      # → JSON string
ReviewResult.model_validate(some_dict)  # dict → model (validates)
```

**Key difference from older Pydantic (v1):** Methods changed names — `.dict()` → `.model_dump()`, `.json()` → `.model_dump_json()`, `.parse_obj()` → `.model_validate()`. This codebase uses v2 exclusively.

### Async / Await (every API endpoint and the AI engine)

```python
import asyncio

# Define an async function
async def fetch_data(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Call from sync code (CLI entry point)
asyncio.run(fetch_data("https://api.example.com"))

# Call from async code (inside another async function)
result = await fetch_data("https://api.example.com")
```

**Pattern in this codebase:** The CLI uses `asyncio.run()` to bridge sync → async. FastAPI endpoints are `async def` natively. The AI engine is async because it makes HTTP calls to the Anthropic API.

### Context Managers

```python
# File I/O — you'll see this pattern throughout the codebase
with path.open(encoding="utf-8") as f:
    data = json.load(f)

# Async context manager — used for HTTP clients and DB connections
async with httpx.AsyncClient(timeout=10.0) as client:
    response = await client.get("/endpoint")

# Custom async context manager (see the FastAPI lifespan in this codebase)
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    # startup code
    yield
    # shutdown code
```

### Path Objects (replaces os.path string manipulation)

```python
from pathlib import Path

# Resolve relative to this file's location (used everywhere in this codebase)
_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

# Common operations
path.exists()          # bool
path.open()            # file handle
path.glob("*.json")    # iterator of matching paths
path.name              # filename with extension
path.stem              # filename without extension
path.suffix            # extension (e.g., ".json")
```

### F-Strings and String Formatting

```python
name = "Paul"
score = 0.85

f"Hello, {name}"                    # basic interpolation
f"Confidence: {score:.0%}"          # → "Confidence: 85%"
f"{'=' * 70}"                       # repeated characters for formatting
f"{result.determination:45s}"       # left-aligned, padded to 45 chars
```

### Walrus Operator and Match Statements (Python 3.10+)

```python
# Walrus operator — assign and test in one expression
if (match := re.search(r"pattern", text)):
    print(match.group(0))

# Match statement (not used in this codebase, but good to know)
match status_code:
    case 200:
        return "OK"
    case 404:
        return "Not found"
    case _:
        return "Other"
```

### Common Imports You'll See

```python
from __future__ import annotations    # enables forward references in type hints
from typing import Any, Literal       # type hint utilities
from collections.abc import AsyncIterator  # abstract base classes (modern location)
from datetime import UTC, datetime     # UTC is new in 3.11 (replaces timezone.utc)
from pathlib import Path               # object-oriented filesystem paths
import json, csv, re, logging, uuid    # standard library workhorses
```

---

## 2. Project Structure & Packaging

> **Open:** `pyproject.toml` (project root) and `src/prior_auth_demo/__init__.py`

### The `src` Layout

```
src/prior_auth_demo/          ← installable package
├── __init__.py               ← package marker (one-line docstring)
├── application_settings.py   ← config (env vars → typed settings)
├── clinical_review_engine.py ← core AI logic (Claude + tools)
├── command_line_demo.py      ← CLI entry point
├── healthcare_api_server.py  ← FastAPI REST API
├── determination_audit_store.py  ← SQLite audit trail
├── mock_healthcare_services/
│   ├── member_eligibility.py ← mock FHIR eligibility endpoint
│   └── load_fhir_data.py    ← Synthea data loader
└── web_dashboard/
    ├── dashboard_routes.py   ← Jinja2 + HTMX routes
    └── templates/            ← HTML templates
```

The `src/` layout means the package isn't importable until installed. `uv sync` installs all dependencies (including dev) and the project in editable mode (see `pyproject.toml`).

### Key `pyproject.toml` Sections

| Section | What It Does |
|---------|-------------|
| `[project]` | Package metadata, Python version (`>=3.12`), dependencies |
| `[project.scripts]` | CLI entry point: `pa-review` → `command_line_demo:main` |
| `[tool.ruff]` | Linter config: line length 120, Python 3.12 target |
| `[tool.mypy]` | Type checker: strict mode enabled |
| `[tool.pytest.ini_options]` | Test markers: `unit`, `integration`, `e2e` |

### Dependencies Worth Knowing

| Package | Purpose | Why This Over Alternatives |
|---------|---------|---------------------------|
| `anthropic` | Claude API client | Direct SDK, no framework wrappers (project constraint) |
| `fastapi` | REST API framework | Async-native, auto-generates OpenAPI docs |
| `pydantic` / `pydantic-settings` | Data validation / config | Type-safe models, env var loading |
| `fhir.resources` | FHIR R4B Pydantic models | BSD-licensed, Pydantic v2 native |
| `httpx` | Async HTTP client | Replaces `requests` for async code |
| `aiosqlite` | Async SQLite | Non-blocking DB access in async FastAPI |
| `jinja2` | HTML templating | Server-side rendering for the dashboard |

---

## 3. Configuration Layer

> **Open:** `application_settings.py`

This is the simplest file in the project — read it first to warm up.

### What to Notice

**`pydantic-settings` BaseSettings** — This class loads config from environment variables or a `.env` file automatically. No manual `os.getenv()` calls.

```python
class ApplicationSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", ...)

    anthropic_api_key: SecretStr = Field(...)          # required (no default)
    claude_model_id: str = Field(default="claude-sonnet-4-6")  # optional w/ default
    auto_approve_confidence_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
```

**Key patterns:**
- `SecretStr` — wraps the API key so it doesn't leak in logs or `.model_dump()` output. Access with `.get_secret_value()`.
- `Field(...)` with `...` (Ellipsis) means the field is **required** — app won't start without it.
- `Field(ge=0.0, le=1.0)` — Pydantic validates the range at construction time.
- `SettingsConfigDict` — replaces Pydantic v1's inner `class Config`.

**How it's used:** Every module that needs config instantiates `ApplicationSettings()` or receives it as a parameter. The settings object is created once and passed around — no global state.

---

## 4. CLI Entry Point — Following a PA Request

> **Open:** `command_line_demo.py`

This is where a PA review starts in the CLI flow. Read it top to bottom — it's the most approachable file.

### Data Flow: CLI Path

```
User runs: uv run python -m prior_auth_demo.command_line_demo --case <file.json>
  │
  ├─ main() parses args with argparse
  ├─ ApplicationSettings() loads config from .env
  ├─ review_single_case() loads the JSON file
  │   ├─ json.load() → raw dict
  │   ├─ Bundle.model_validate(data) → FHIR Bundle (Pydantic validation)
  │   ├─ review_prior_auth_request(bundle, settings) → ClinicalReviewResult
  │   └─ print_result() → formatted terminal output
  └─ asyncio.run() bridges sync main() to async engine
```

### Patterns to Study

**argparse with mutually exclusive groups** (lines ~298-308):
```python
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--case", type=str, ...)
group.add_argument("--all", action="store_true", ...)
group.add_argument("--inspect", type=str, ...)
```
Only one of `--case`, `--all`, or `--inspect` can be used. `required=True` means you must pick one.

**Threading for UI spinner** (lines ~71-83): A background thread shows a progress spinner while the async AI review runs. `threading.Event` coordinates start/stop — `stop_event.wait(0.5)` replaces `time.sleep()` so the thread can be interrupted instantly.

**FHIR Bundle validation** (line ~145):
```python
bundle = Bundle.model_validate(data)
```
This single line validates the entire JSON structure against the FHIR R4B Bundle schema. If the JSON is malformed or missing required FHIR fields, Pydantic raises `ValidationError`. This is the bridge between raw JSON and typed healthcare data.

**The `if __name__ == "__main__"` guard** (lines ~320-321): Standard Python entry point pattern. Also note the `[project.scripts]` entry in `pyproject.toml` that maps `pa-review` → `main()` for installed use.

**Windows Unicode handling** (lines ~22-23): The `sys.stdout` wrapper at the top ensures Unicode characters (like ANSI codes) work on Windows terminals — a real-world concern you'd encounter at Autonomize.

---

## 5. The AI Engine — Core Business Logic

> **Open:** `clinical_review_engine.py`

This is the most important file. It contains the core AI orchestration — the pattern you'd extend or replicate in a live coding session.

### Data Flow: AI Review

```
review_prior_auth_request(bundle, settings)
  │
  ├─ _extract_claim_from_bundle(bundle) → claim dict
  ├─ Create AsyncAnthropic client with API key
  ├─ Serialize bundle to JSON for Claude's context
  │
  ├─ TOOL USE LOOP (up to 10 iterations):
  │   ├─ Send messages + tool definitions to Claude
  │   ├─ If Claude calls a tool:
  │   │   ├─ _dispatch_tool() routes to the right handler
  │   │   │   ├─ validate_npi() → Luhn-10 check
  │   │   │   ├─ lookup_icd10_code() → TSV file lookup
  │   │   │   ├─ check_cms_coverage() → JSON file lookup
  │   │   │   └─ retrieve_clinical_data() → FHIR Bundle extraction
  │   │   └─ Tool results appended to conversation
  │   └─ If Claude returns final text: break
  │
  ├─ _parse_determination(final_text) → structured dict
  ├─ apply_confidence_routing() → possibly downgrade to PENDED
  ├─ _build_claim_response() → FHIR ClaimResponse
  └─ Return ClinicalReviewResult (Pydantic model)
```

### Section by Section

#### Data Models (lines ~30-46)

```python
class ClinicalReviewResult(BaseModel):
    determination: Literal["APPROVED", "DENIED", "PENDED_FOR_REVIEW", "PENDED_MISSING_INFO"]
    confidence_score: float = Field(ge=0.0, le=1.0)
    ...
    fhir_claim_response: ClaimResponse  # nested FHIR model
```

The `Literal` type restricts `determination` to exactly four values — Pydantic rejects anything else. The `ClaimResponse` is a FHIR Pydantic model from `fhir.resources.R4B`.

#### Tool Handler Functions (lines ~53-169)

Four pure functions that Claude can invoke during its analysis:

| Function | Input | Output | Data Source |
|----------|-------|--------|-------------|
| `validate_npi(npi)` | 10-digit string | `{valid, npi, reason}` | Algorithmic (Luhn-10) |
| `lookup_icd10_code(code)` | ICD-10 code | `{code, description}` | Local TSV file |
| `check_cms_coverage(code)` | CPT/HCPCS code | Coverage criteria dict | Local JSON file |
| `retrieve_clinical_data(bundle)` | FHIR Bundle | Extracted patient data | In-memory Bundle |

**The Luhn-10 algorithm** (lines ~89-103) is worth understanding — it's the same checksum algorithm used for credit card validation, but with the CMS `80840` prefix per 45 CFR 162.406. This is a good example of domain-specific validation logic.

**File I/O pattern** — `lookup_icd10_code` uses `csv.DictReader` with tab delimiter; `check_cms_coverage` uses `json.load`. Both resolve paths relative to the package using `Path(__file__).resolve()`.

#### Claude Tool Definitions (lines ~236-306)

The `TOOL_DEFINITIONS` list follows the Anthropic API's tool schema — each tool has a `name`, `description`, and `input_schema` (JSON Schema). Claude reads these descriptions to decide which tools to call and what arguments to pass.

**This is the Anthropic SDK pattern you need to know for the interview.** The tool definitions are the contract between your Python code and Claude's reasoning.

#### The System Prompt (lines ~311-363)

A multi-line string that instructs Claude how to behave as a clinical reviewer. Notice:
- It tells Claude the **order** of tool calls (retrieve data first, then validate, then check coverage)
- It defines the **determination rules** (business logic Claude follows)
- It specifies the **response format** (JSON with exact field names)

#### The Main Engine Function (lines ~369-479)

`review_prior_auth_request` is the orchestrator. Key patterns:

**Anthropic SDK tool-use loop** (lines ~406-437):
```python
for _ in range(max_iterations):
    response = await client.messages.create(
        model=settings.claude_model_id,
        system=SYSTEM_PROMPT,
        tools=TOOL_DEFINITIONS,
        messages=messages,
    )
    if response.stop_reason == "tool_use":
        # dispatch tools, append results, loop again
    else:
        break  # Claude is done — has final answer
```

This is the canonical Anthropic tool-use pattern: send, check if Claude wants to use a tool, execute the tool, return the result, repeat until Claude produces a final text response.

**`_dispatch_tool`** (lines ~485-513) is a simple router — maps tool names to Python functions. In a production system, you'd use a registry pattern; for a demo, the if/elif chain is appropriate.

**`_parse_determination`** (lines ~526-574) uses three fallback strategies to extract JSON from Claude's response: markdown code blocks, regex for JSON with a `"determination"` key, and brace-matching. The fallback returns `PENDED_FOR_REVIEW` — never auto-denies on parse failure.

#### Confidence Routing (lines ~207-231)

```python
def apply_confidence_routing(raw_determination, confidence, ...):
    if raw_determination in ("DENIED", "PENDED_MISSING_INFO", "PENDED_FOR_REVIEW"):
        return raw_determination        # preserve explicit decisions
    if raw_determination == "APPROVED":
        if confidence >= auto_approve_threshold:
            return "APPROVED"            # high confidence → auto-approve
        return "PENDED_FOR_REVIEW"       # low confidence → human review
    return "PENDED_FOR_REVIEW"           # unknown → safe default
```

**Key design decision:** The system never auto-denies. Low confidence always routes to human review. This is a healthcare AI safety pattern — the Autonomize team will care about this.

---

## 6. FastAPI REST API — HTTP Entry Point

> **Open:** `healthcare_api_server.py`

This file creates the FastAPI application and defines the REST endpoints. It's the HTTP equivalent of the CLI — same engine, different entry point.

### Data Flow: API Path

```
POST /api/v1/prior-auth/review  (FHIR Bundle JSON body)
  │
  ├─ FastAPI validates request body (dict[str, Any])
  ├─ Bundle.model_validate(request_body) → FHIR validation
  ├─ Check for Claim resource in Bundle
  ├─ _ensure_initialized() → lazy-load settings + audit store
  ├─ review_prior_auth_request(bundle, settings) → ClinicalReviewResult
  ├─ audit_store.store_determination(...) → SQLite append
  └─ Return JSON response with audit_id
```

### Patterns to Study

**FastAPI application lifecycle** (lines ~233-250):
```python
@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    await _ensure_initialized()  # startup
    yield                        # app runs
    if _audit_store:
        await _audit_store.close()  # shutdown
```
The `lifespan` context manager replaces FastAPI's older `on_startup`/`on_shutdown` events. Everything before `yield` runs on startup; everything after runs on shutdown.

**Lazy initialization** (lines ~222-230): `_ensure_initialized()` creates the settings and audit store on first use. This handles both the production lifespan and test environments where lifespan may not run.

**Router composition** (lines ~286-291):
```python
app.include_router(eligibility_router, prefix="/mock/eligibility")
app.include_router(dashboard_router)
```
FastAPI routers are modular — each sub-module defines its own routes, and the main app mounts them with optional prefixes. This is how the mock services and dashboard are wired in without cluttering the main file.

**Request validation** (lines ~395-415):
```python
async def review_pa_request(
    request_body: dict[str, Any] = Body(examples=[_REVIEW_EXAMPLE_VALUE]),
) -> dict[str, Any]:
    bundle = Bundle.model_validate(request_body)  # FHIR validation
```
The `Body(examples=[...])` parameter pre-fills the Swagger UI with a working example so evaluators can click "Try it out" → "Execute" without crafting a FHIR Bundle by hand.

**OpenAPI documentation** (tags, summary, description on every endpoint): FastAPI auto-generates interactive docs at `/docs` (Swagger) and `/redoc`. The tags group endpoints in the UI. This is why the endpoint decorators are verbose — it's the developer experience layer.

**Path traversal prevention** (lines ~366-370):
```python
case_path = (_SAMPLE_CASES_DIR / name).resolve()
if not case_path.is_relative_to(_SAMPLE_CASES_DIR.resolve()):
    raise HTTPException(status_code=404, ...)
```
`is_relative_to()` ensures the resolved path is still inside the sample cases directory, preventing `../../etc/passwd` attacks. Standard secure coding practice.

---

## 7. Audit Store — Async SQLite

> **Open:** `determination_audit_store.py`

This file implements the append-only audit trail — a compliance requirement for healthcare AI systems.

### Patterns to Study

**Async SQLite with `aiosqlite`** — SQLite is synchronous by nature. `aiosqlite` wraps it in a thread pool so it doesn't block FastAPI's event loop. The API mirrors standard `sqlite3` but with `await`:

```python
self._db = await aiosqlite.connect(self._db_path)
await self._db.execute("INSERT INTO ...", params)
await self._db.commit()
cursor = await self._db.execute("SELECT * FROM ...")
rows = await cursor.fetchall()
```

**Row factory** (line ~33): `self._db.row_factory = aiosqlite.Row` makes rows behave like dicts — you can access columns by name instead of index.

**UUID primary keys** (line ~64): `str(uuid.uuid4())` generates globally unique IDs. No auto-increment — each determination gets a random UUID, which is standard for distributed systems.

**Append-only design** — Notice there are no `UPDATE` or `DELETE` methods. This is intentional for audit compliance. The class has exactly four operations: `init_db`, `store_determination`, `get_determination`, `list_determinations`.

**JSON serialization for list columns** (lines ~79, ~98): `guideline_citations` is a Python list stored as a JSON string in SQLite. Serialized with `json.dumps()` on write, deserialized with `json.loads()` on read.

**Resource cleanup pattern** (lines ~117-121):
```python
async def close(self) -> None:
    if self._db:
        await self._db.close()
        self._db = None
```
Called from the FastAPI lifespan's shutdown phase. Setting `self._db = None` prevents double-close errors.

---

## 8. Mock Healthcare Services

> **Open:** `mock_healthcare_services/member_eligibility.py`, then `mock_healthcare_services/load_fhir_data.py`

### Member Eligibility (member_eligibility.py)

A single-endpoint FastAPI router that returns a FHIR `CoverageEligibilityResponse`. Every member is eligible — this mocks what would be a Payer Core System (TriZetto, QNXT, etc.) in production.

**Pattern:** `APIRouter` — defines routes independently, mounted into the main app with `app.include_router()`.

### FHIR Data Loader (load_fhir_data.py)

Loads Synthea-generated FHIR NDJSON files into a HAPI FHIR server via HTTP PUT.

**Patterns to study:**

- **NDJSON processing** — each line is a complete JSON object (one resource per line)
- **Dependency ordering** — `_PRIORITY_ORDER` loads Organizations before Patients before Claims, satisfying FHIR reference integrity
- **Custom sort key** — `sort_key()` returns a tuple `(priority_group, name)` for multi-level sorting
- **HTTP PUT for upserts** — `PUT /{ResourceType}/{id}` creates or updates a resource (idempotent)
- **Script entry point** — `if __name__ == "__main__"` + `asyncio.run(main())` pattern for standalone execution

---

## 9. Web Dashboard — Server-Side Rendering

> **Open:** `web_dashboard/dashboard_routes.py`

The dashboard uses Jinja2 templates with HTMX for interactivity — no custom JavaScript.

### Patterns to Study

**Jinja2Templates setup** (lines ~23-25):
```python
_TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(_TEMPLATE_DIR))
```

**Template rendering** (lines ~41-46):
```python
return templates.TemplateResponse(
    request=request,          # FastAPI requires this
    name="review_dashboard.html",
    context={"cases": DEMO_CASES},  # variables available in template
)
```

**HTMX pattern** — The `POST /dashboard/review` endpoint returns an HTML *fragment* (not a full page). HTMX swaps this fragment into the existing page without a full reload. The `GET /dashboard/history` endpoint returns table row fragments for the same reason.

**Cross-module import** (line ~54): The dashboard imports `_ensure_initialized` from `healthcare_api_server` to share the singleton settings and audit store. This is a pragmatic demo choice — in production, you'd use dependency injection.

---

## 10. Testing Patterns

> **Open:** `tests/conftest.py` and any `tests/test_*.py` file

The test suite uses `pytest` with `pytest-asyncio` for async tests and `polyfactory` for generating test data from Pydantic models.

### Key Conventions

```python
@pytest.mark.unit          # no external dependencies
@pytest.mark.integration   # requires FHIR server or API
@pytest.mark.e2e           # full system test

# Async tests — pytest-asyncio handles the event loop
async def test_something():
    result = await some_async_function()
    assert result.determination == "APPROVED"

# Every test has a docstring explaining what it verifies
async def test_npi_validation_rejects_short_input():
    """NPI validation should reject strings shorter than 10 digits."""
    result = validate_npi("12345")
    assert result["valid"] is False
```

### What to Know for Live Coding

If asked to add a new function, you'll likely need to write a test too. The pattern is:
1. Create a test function with a descriptive name and docstring
2. Call the function under test
3. Assert the expected behavior
4. Use `@pytest.mark.unit` for pure logic tests

---

## 11. Live Coding Cheat Sheet

> **No file to open.** This is your quick reference for extending this application.

### Adding a New Tool to the AI Engine

1. **Write the handler function** in `clinical_review_engine.py`:
   ```python
   def my_new_tool(param: str) -> dict[str, Any]:
       """Docstring explaining what this tool does."""
       # implementation
       return {"result": "value"}
   ```

2. **Add the tool definition** to `TOOL_DEFINITIONS`:
   ```python
   {
       "name": "my_new_tool",
       "description": "What Claude should know about this tool",
       "input_schema": {
           "type": "object",
           "properties": {"param": {"type": "string", "description": "..."}},
           "required": ["param"],
       },
   }
   ```

3. **Add dispatch routing** in `_dispatch_tool`:
   ```python
   elif tool_name == "my_new_tool":
       return my_new_tool(tool_input["param"])
   ```

4. **Write a test** in `tests/test_clinical_review_engine.py`.

### Adding a New API Endpoint

```python
@app.post("/api/v1/my-endpoint", tags=["My Feature"])
async def my_endpoint(data: MyModel) -> dict[str, Any]:
    """Endpoint docstring."""
    settings, audit_store = await _ensure_initialized()
    # business logic
    return {"status": "ok"}
```

### Adding a New Pydantic Model

```python
from pydantic import BaseModel, Field

class MyModel(BaseModel):
    """What this model represents."""
    required_field: str
    optional_field: int = Field(default=0, ge=0)
    nullable_field: str | None = None
```

### Common Operations Quick Reference

| Task | Code |
|------|------|
| Load JSON file | `with path.open() as f: data = json.load(f)` |
| Validate FHIR Bundle | `bundle = Bundle.model_validate(data)` |
| Make async HTTP call | `async with httpx.AsyncClient() as c: r = await c.get(url)` |
| Return error from API | `raise HTTPException(status_code=404, detail="Not found")` |
| Log with context | `logger.info("Processed %s: %s", case_name, result)` |
| Generate UUID | `import uuid; str(uuid.uuid4())` |
| Current UTC time | `from datetime import UTC, datetime; datetime.now(UTC)` |
| Run async from sync | `asyncio.run(my_async_function())` |

### Python Gotchas to Remember

1. **Mutable default arguments** — Never `def f(items=[])`. Use `def f(items: list | None = None)` and `items = items or []` inside.
2. **`async def` vs `def`** in FastAPI — Both work, but `async def` is required if you `await` anything inside. Don't mix blocking I/O in `async def` without `run_in_executor`.
3. **`model_dump()` not `.dict()`** — Pydantic v2 renamed these methods.
4. **f-string debugging** — `f"{variable=}"` prints both name and value: `x=42`.
5. **Type narrowing** — `if result is not None:` lets mypy know `result` is no longer `None` in that branch.

---

## Summary: How Everything Connects

```
                    ┌─────────────────────┐
                    │  application_       │
                    │  settings.py        │
                    │  (env vars → config)│
                    └────────┬────────────┘
                             │ settings injected into
                    ┌────────┴────────────┐
     CLI path       │                     │  API path
  ┌─────────────────┤                     ├──────────────────┐
  │                 │  clinical_review_   │                  │
  │                 │  engine.py          │                  │
  │                 │  (Claude + tools)   │                  │
  │                 └────────┬────────────┘                  │
  │                          │                               │
  │                          │ ClinicalReviewResult          │
  │                          │                               │
command_line_      ┌─────────┴──────────┐      healthcare_
demo.py            │ determination_     │      api_server.py
(argparse →        │ audit_store.py     │      (FastAPI →
 terminal output)  │ (SQLite append)    │       JSON response)
                   └────────────────────┘            │
                                                     │
                                              web_dashboard/
                                              dashboard_routes.py
                                              (Jinja2 + HTMX →
                                               HTML fragments)
```

Every path through the system ends at the same engine. The CLI, API, and dashboard are just different entry points. If you understand `clinical_review_engine.py`, you understand the core of this application.
