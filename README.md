# Conchalabs-API

Conchalabs take-home project. This application consists of a REST API built using Python and a Postgres database.

## Stack

* FastAPI
* SqlModel
* asyncpg
* alembic
* Terraform

## Running locally

### Running using Docker

You can start both the API and the database using the docker compose file:

```bash
docker-compose up api
```

The compose file will also run the migration job to create the tables on the database. 
The API docs will be available at http://localhost:8000/docs.

### Running on the local environment

Ensure you have Python 3.11 installed on your machine. If not, you can install it using [Pyenv](https://github.com/pyenv/pyenv).

```bash
pyenv install 3.11
pyenv shell 3.11
```

If you don't have a Postgres database running on your machine, you can start the database provided on the docker compose file:

```bash
docker-compose up -d database
```

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install the dev dependencies:

```bash
make requirements-dev
```

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

The `.env` will be pointing to the database from the docker compose, then if you're using your own database 
you need to change the `DATABASE_URL` to match your database information.
Then, run the migrations:

```bash
make migrate
```

Finally, you can start the API using the command:

```bash
make run-dev
```

The API documentation will be available at http://localhost:8000/docs.

## Quality checks

To run the linters to check and fix code standardization:

```bash
make lint
```

You can run the tests using the docker compose file:

```bash
docker-compose up test
```

It will automatically start the database, run the migrations and run the test suite.

You can also run them locally: 

```bash
make test
```

And generate the project test coverage report:

```bash
make coverage-html
```

The report will be available at htmlcov/index.html.

> **Note**: the report is showing some lines uncovered, but it seems to be pytest-cov + async tests weird behavior.

## Migrations

Every time a model is created or changed the create-migrations needs to run to create the migration file:

```bash
make create-migrations
```

Then apply the new migration by running migrate:

```bash
make migrate
```

> **Note**: when a new model is created the file `migrations/env.py` needs to be updated to import the new model as well.
> This is a required step so alembic can detect the model.

## Deploy

The application can be automatically deployed to GCP using Terraform.

### Pre-requisites

* Install terraform CLI and initialize it (`terraform init`)
* Install gcloud CLI and log-in in your account
* Create a service account on GCP with the following roles: Editor, Cloud Run Admin, Compute network admin and download the credentials file. 
* Configure Google Cloud Registry on your docker CLI (`gcloud auth configure-docker`)

### Steps

First, create the file `environments/gcp/terraform.tfvars` and fill with the specific values of your GCP project. Example:

```terraform
project           = "conchalabs"
region            = "southamerica-east1"
zone              = "southamerica-east1-a"
credentials_file  = "/path/to/service-account-credentials.json"
database_name     = "conchalabsdb"
database_user     = "admin"
database_password = "conchalabs"
app_image         = "gcr.io/conchalabs/conchalabs-api"
migration_image   = "gcr.io/conchalabs/conchalabs-migration"
```

Use the commands to build the API and migration images and push them to Google Cloud Registry:

```bash
make build-api-gcp
make build-migration-gcp
```

Deploy all the resources to your GCP project (this might time some time, so grab some coffee):

```bash
make deploy-gcp
```

When it finishes, the API URL created will be displayed to you. 

> **Note**: Some GCP APIs accesses might still be requested by the CLI as the resources are created.
> Just enable the API on the project and run the command again.

Last but not least, run the migration job to create the tables on the database:

```bash
make migrate-gcp
```

## To Do

* Find out why coverage is not hitting all the lines
* Add some nice logs
* Add authentication/authorization using protocols like OAuth/OpenID to secure the APIs
* Create a CI/CD pipeline to check the code and automate the application deploy on GCP from the repository
* Create a bucket on GCP to store the infrastructure state
* As the application grow, it would be interesting to create a new layer for the business logic