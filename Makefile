requirements-dev:
	pip install -r requirements/dev.txt

run-dev:
	uvicorn conchalabs.app:app --reload

check-lint:
	isort . --check-only --profile black
	black . -t py311 --check
	mypy conchalabs --ignore-missing-imports

lint:
	isort . --profile black
	black . -t py311
	mypy conchalabs --ignore-missing-imports

create-migrations:
	alembic revision --autogenerate

migrate:
	alembic upgrade head

test: migrate
	pytest --asyncio-mode=auto

coverage: migrate
	pytest --asyncio-mode=auto --cov=conchalabs --cov-fail-under=85

coverage-html: migrate
	pytest --asyncio-mode=auto --cov=conchalabs --cov-report=html --cov-fail-under=85

build-dev:
	docker build -f dev.dockerfile -t conchalabs-api .

build-api-gcp:
	docker build -f api.dockerfile --platform linux/amd64 -t gcr.io/conchalabs/conchalabs-api .
	docker push gcr.io/conchalabs/conchalabs-api

deploy-gcp:
	terraform -chdir=environments/gcp apply

build-migration-gcp:
	docker build -f migration.dockerfile --platform linux/amd64 -t gcr.io/conchalabs/conchalabs-migration .
	docker push gcr.io/conchalabs/conchalabs-migration

migrate-gcp:
	gcloud beta run jobs execute migration-job --wait
