.PHONY: install dev test clean lint format check

install:
	pip install -e ".[dev]"

dev:
	uvicorn src.main:app --reload --port 8000

test:
	pytest -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache *.egg-info dist build

lint:
	ruff check src/ tests/
	mypy src/

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/

check: lint test
