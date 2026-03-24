.PHONY: install dev test clean lint format check review review-all download-synthea

install:
	pip install -e ".[dev]"
	pre-commit install

dev:
	uvicorn prior_auth_demo.healthcare_api_server:app --reload --port 8000

review:
	python -m prior_auth_demo.command_line_demo

review-all:
	python -m prior_auth_demo.command_line_demo --all

test:
	pytest -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache *.egg-info dist build

lint:
	ruff check src/prior_auth_demo/ tests/
	ruff format --check src/prior_auth_demo/ tests/
	mypy src/prior_auth_demo/

format:
	ruff format src/prior_auth_demo/ tests/
	ruff check --fix src/prior_auth_demo/ tests/

check: lint test

download-synthea:
	git clone --branch 10-patients --single-branch --depth 1 \
		https://github.com/smart-on-fhir/sample-bulk-fhir-datasets.git \
		data/synthea_fhir_patients/raw
