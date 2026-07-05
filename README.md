# SmartComply Backend

SmartComply is a transaction monitoring and compliance platform that evaluates financial transactions against configurable risk rules. The system assigns a risk score, generates compliance alerts, records audit logs, and classifies customers as high risk based on observed transaction behaviour rather than user-provided input.

---

# Features

* JWT authentication using Simple JWT
* Customer management
* Transaction processing
* Rule-based compliance engine
* Automatic risk scoring
* Automatic customer risk classification
* Alert generation
* Audit logging
* OpenAPI documentation with DRF Spectacular
* Unit and integration tests using Pytest

---

# Technology Stack

| Component         | Technology            |
| ----------------- | --------------------- |
| Framework         | Django 5              |
| API               | Django REST Framework |
| Authentication    | Simple JWT            |
| Database          | PostgreSQL            |
| Message Broker    | Redis                 |
| Event Processing  | Kafka                 |
| API Documentation | DRF Spectacular       |
| Testing           | Pytest                |
| Production Server | Gunicorn              |

---

# Setup Instructions

## Prerequisites

Install the following software before running the project.

* Python 3.12+
* PostgreSQL
* Redis
* Kafka (for event publishing)

---

## Clone Repository

```bash
git clone <repository_url>
cd backend
```

---

## Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows

```bash
.venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file.

```env
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=*

DB_NAME=smartcomply
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

REDIS_HOST=localhost
REDIS_PORT=6379

KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

---

## Apply Migrations

```bash
python manage.py migrate
```

---

## Create Administrator

```bash
python manage.py createsuperuser
```

---

## Run Development Server

```bash
python manage.py runserver
```

The API is available at

```
http://127.0.0.1:8000/
```

---

# Docker

The backend includes a production-ready multi-stage Dockerfile and a Docker Compose configuration for local development.

## Prerequisites

- Docker
- Docker Compose

## Build and Start

```bash
docker compose up --build
```

This starts:

- Django API
- PostgreSQL
- Redis

The API will be available at:

```
http://localhost:8000
```

---

## Run in Detached Mode

```bash
docker compose up -d
```

---

## Stop Containers

```bash
docker compose down
```

---

## Remove Volumes

```bash
docker compose down -v
```

---

## View Logs

```bash
docker compose logs -f
```

For a specific service:

```bash
docker compose logs -f web
```

---

## Run Management Commands

Create a superuser:

```bash
docker compose exec web python manage.py createsuperuser
```

Open a Django shell:

```bash
docker compose exec web python manage.py shell
```

Run tests:

```bash
docker compose exec web pytest
```

Run migrations manually:

```bash
docker compose exec web python manage.py migrate
```

---

## Docker Services

| Service | Description |
|----------|-------------|
| **web** | Django application served with Gunicorn |
| **db** | PostgreSQL database |
| **redis** | Redis cache and message broker |

The Docker entrypoint automatically:

1. Applies database migrations.
2. Collects static files.
3. Starts Gunicorn.

This allows the application to be started with a single `docker compose up` command.

---

## API Documentation

Swagger

```
http://127.0.0.1:8000/api/schema/swagger-ui/
```

OpenAPI Schema

```
http://127.0.0.1:8000/api/schema/
```

---

# Running Tests

Run all tests

```bash
pytest
```

Run a specific module

```bash
pytest transactions/tests.py
```

Run a single test

```bash
pytest transactions/tests.py::test_create_transaction_high_risk
```

---

# Project Structure

```
backend/

├── alerts/
├── audit/
├── authentication/
├── common/
├── config/
├── customers/
├── dashboard/
├── rules/
├── transactions/
├── worker/
└── manage.py
```

### Module Responsibilities

| Module         | Responsibility                                   |
| -------------- | ------------------------------------------------ |
| authentication | JWT authentication                               |
| customers      | Customer management                              |
| transactions   | Transaction CRUD and processing                  |
| rules          | Compliance rule engine                           |
| alerts         | Generated compliance alerts                      |
| audit          | Immutable audit trail                            |
| dashboard      | Aggregated statistics                            |
| common         | Shared models and utilities                      |
| worker         | Kafka event publishing and background processing |
| config         | Django configuration                             |

---

# Architecture Overview

The application follows a layered architecture to separate responsibilities.

```
             Client
                │
                ▼
        Django REST Views
                │
                ▼
        Serializers (Validation)
                │
                ▼
      Service Layer (Business Logic)
                │
        ┌───────┴────────┐
        ▼                ▼
 Rule Engine        Database
        │
        ▼
 Risk Score
        │
        ▼
 Alerts + Audit Logs
        │
        ▼
 Kafka Event Publisher
```

### Request Flow

1. Client submits a transaction.
2. Serializer validates incoming data.
3. TransactionService persists the transaction.
4. The Rule Engine evaluates every registered rule.
5. A cumulative risk score is calculated.
6. Triggered rules generate alerts.
7. Audit logs are written.
8. Customers exceeding the configured threshold are automatically classified as high risk.
9. A Kafka event is published for downstream consumers.

---

# Rule Engine

The compliance engine discovers registered rules dynamically.

Each rule returns:

* Whether it triggered
* Risk score contribution
* Severity
* Alert message

Example rules include:

* High transaction amount
* High-risk customer
* Transaction velocity
* Blacklisted country

New rules can be added by simply implementing the `Rule` interface without modifying existing business logic.

---

## Design Decisions

## Service Layer

Business logic is separated from API views.

Benefits:

* Easier testing
* Reusable business logic
* Thin controllers
* Better maintainability

---

## Rule Engine

Rules are independent classes implementing a common interface.

Benefits:

* Open for extension
* Easy to test individually
* No large conditional blocks
* Supports plug-and-play rules

---

## Automatic Risk Classification

Customers are **not allowed** to declare themselves as high risk.

Instead, the backend derives customer risk from transaction history and compliance rules.

This prevents malicious users from manipulating their own risk profile.

---

## Event-Driven Processing

After successful transaction creation, an event is published to Kafka.

Benefits:

* Loose coupling
* Easy integration with external systems
* Future support for notifications, analytics and monitoring

---

## Audit Logging

Every compliance evaluation generates an immutable audit record.

This provides traceability and supports compliance investigations.

---

# Trade-offs

### Rule Evaluation is Synchronous

Rules currently execute during transaction creation.

Advantages

* Immediate response
* Immediate risk score
* Simpler implementation

Disadvantages

* Higher request latency
* Less scalable under heavy load

A production deployment could move rule evaluation entirely to background workers.

---

### High Risk Threshold

Customers become high risk when the cumulative risk score reaches the configured threshold.

Advantages

* Simple
* Easy to understand

Disadvantages

* Static thresholds may not adapt well to changing fraud patterns.

Future versions could replace this with configurable thresholds or machine learning.

---

### Database-Centric Design

Risk scores, alerts and audit logs are persisted immediately.

Advantages

* Consistent reporting
* Easy querying
* Historical tracking

Disadvantages

* Increased write operations during transaction processing.

---

# Assumptions

The implementation makes the following assumptions:

* Customer email addresses are unique.
* Transactions are immutable after completion except for administrative updates.
* Every transaction belongs to exactly one customer.
* Rule failures should not prevent transaction creation; failed rules are logged and remaining rules continue executing.
* High-risk classification is determined only by backend business rules.
* Kafka is available for event publishing in production.
* Authentication is performed using JWT access and refresh tokens.
* PostgreSQL is the primary production database.

---

# Future Improvements

* Configurable compliance rules from the admin dashboard
* Rule weighting stored in the database
* Machine learning fraud detection
* Asynchronous rule execution
* Email and SMS notifications
* Alert assignment workflow
* Customer risk history
* Real-time dashboards using WebSockets or Server-Sent Events
* Multi-tenant support

---

# Development Commands

| Command                            | Description               |
| ---------------------------------- | ------------------------- |
| `python manage.py runserver`       | Start development server  |
| `python manage.py migrate`         | Apply database migrations |
| `python manage.py createsuperuser` | Create administrator      |
| `python manage.py check`           | Run Django system checks  |
| `pytest`                           | Run all tests             |
| `pytest transactions/tests.py`     | Run transaction tests     |
| `flake8 .`                         | Run linting               |
