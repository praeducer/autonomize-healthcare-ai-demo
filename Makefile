.PHONY: install dev test clean lint format check review review-all download-synthea test-unit test-integration test-e2e test-data-quality test-all up down load-fhir-data fhir-reset fhir-status setup-fhir

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
	@echo "Waiting for HAPI FHIR server to be healthy..."
	@timeout=120; while [ $$timeout -gt 0 ]; do \
		if docker inspect --format='{{.State.Health.Status}}' hapi-fhir-demo 2>/dev/null | grep -q healthy; then \
			echo "HAPI FHIR server is healthy!"; \
			break; \
		fi; \
		sleep 2; \
		timeout=$$((timeout - 2)); \
	done; \
	if [ $$timeout -le 0 ]; then \
		echo "ERROR: FHIR server did not become healthy in 120s"; \
		docker compose logs fhir-server | tail -20; \
		exit 1; \
	fi

down:
	docker compose down

fhir-reset:
	docker compose down -v
	docker compose up -d
	@$(MAKE) --no-print-directory up 2>/dev/null || true
	@echo "FHIR data volume cleared. Run 'make load-fhir-data' to reload."

load-fhir-data:
	python -m prior_auth_demo.mock_healthcare_services.load_fhir_data

fhir-status:
	@docker inspect --format='Container: {{.Name}} | Status: {{.State.Status}} | Health: {{.State.Health.Status}}' hapi-fhir-demo 2>/dev/null || echo "HAPI FHIR container not running"

setup-fhir: up load-fhir-data
	@echo ""
	@echo "HAPI FHIR server ready at http://localhost:8080"
	@echo "FHIR endpoint: http://localhost:8080/fhir"
	@echo "Synthea patient data loaded."
