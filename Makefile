.PHONY: install dev test clean lint format check review review-all download-synthea test-unit test-integration test-e2e test-data-quality test-all up down load-fhir-data

install:
	pip install -e ".[dev]"
	pre-commit install

dev:
	uvicorn prior_auth_demo.healthcare_api_server:app --reload --port 8000

review:
	python -m prior_auth_demo.command_line_demo --case data/sample_pa_cases/01_lumbar_mri_clear_approval.json

review-all:
	python -m prior_auth_demo.command_line_demo --all

test:
	pytest -v

test-unit:
	pytest tests/ -m unit -v

test-integration:
	pytest tests/ -m integration -v

test-e2e:
	pytest tests/ -m e2e -v --timeout=300

test-data-quality:
	pytest tests/test_data_quality.py -v

test-all:
	pytest tests/ -v --timeout=300

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

up:
	docker compose up -d

down:
	docker compose down

load-fhir-data:
	python -m prior_auth_demo.mock_healthcare_services.load_fhir_data
