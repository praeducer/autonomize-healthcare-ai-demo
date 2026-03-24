# AI-Driven Prior Authorization Demo

## Project Context

Interview exercise for Autonomize AI demonstrating AI-driven prior authorization automation. This is a **demo-scope prototype** — not the full enterprise architecture.

**Full architecture**: `../solutions-architecture-agent/outputs/eng-2026-004-v2/solution-architecture-source-of-truth.md`
**Implementation spec**: `../solutions-architecture-agent/outputs/eng-2026-004-v2/plans/demo-implementation-prompt.md`

**Owner**: Paul Prae — Modular Earth LLC (www.paulprae.com)

## Coding Standards

- Python 3.12 with type hints on all function signatures
- Pydantic v2 models for all data structures
- Async FastAPI endpoints
- Ruff for linting and formatting (`ruff check`, `ruff format`)
- Module docstrings on every file explaining purpose
- No commented-out code — delete or implement
- Environment config via `os.environ`

## Testing

```bash
make test              # Run all tests
pytest tests/ -v       # Verbose output
```
