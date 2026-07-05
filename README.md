# SmartComply Backend

SmartComply is a transaction monitoring and compliance platform that evaluates financial transactions against configurable risk rules. The system assigns a cumulative risk score, generates compliance alerts, records audit logs, and automatically classifies customers as high risk based on transaction behaviour. Compliance processing is performed asynchronously using Redis Streams and a background worker.

---

# Features

- JWT authentication using Simple JWT
- Customer management
- Transaction processing
- Rule-based compliance engine
- Automatic risk scoring
- Automatic customer risk classification
- Alert generation
- Audit logging
- Asynchronous event processing using Redis Streams
- Background worker for compliance evaluation
- Database seed command for generating sample data
- OpenAPI documentation with DRF Spectacular
- Unit and integration tests using Pytest

---

# Technology Stack

| Component | Technology |
|-----------|------------|
| Framework | Django 5 |
| API | Django REST Framework |
| Authentication | Simple JWT |
| Database | PostgreSQL |
| Cache & Event Streaming | Redis (Redis Streams) |
| Background Processing | Django Management Commands |
| API Documentation | DRF Spectacular |
| Testing | Pytest |
| Production Server | Gunicorn |

---

# Setup Instructions

## Prerequisites

Install the following software before running the project.

- Python 3.12+
- PostgreSQL
- Redis
- Docker (optional)
- Docker Compose (optional)

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
```

---

## Apply Migrations

```bash
python manage.py migrate
```

---

## Seed Sample Data

Populate the database with customers and transactions for local development.

```bash
python manage.py seed
```

You can optionally specify the number of customers and transactions.

```bash
python manage.py seed --customers 20 --transactions 200
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

The API will be available at

```
http://127.0.0.1:8000/
```

---

# Running the Background Worker

Compliance processing is handled asynchronously by a Redis Streams consumer.

Start the worker using:

```bash
python manage.py consumer
```

The worker continuously listens for newly created transaction events and performs:

- Rule evaluation
- Risk score calculation
- Alert generation
- Audit logging
- Customer risk classification

---

# Docker

The backend includes a production-ready multi-stage Dockerfile together with Docker Compose for local development.

## Build and Start

```bash
docker compose up --build
```

This starts:

- Django API
- PostgreSQL
- Redis

The API will be available at

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

## Running the Worker in Docker

Start the worker inside the application container.

```bash
docker compose exec web python manage.py consumer
```

---

## Run Management Commands

Create a superuser

```bash
docker compose exec web python manage.py createsuperuser
```

Seed sample data

```bash
docker compose exec web python manage.py seed
```

Open a Django shell

```bash
docker compose exec web python manage.py shell
```

Run tests

```bash
docker compose exec web pytest
```

Apply migrations

```bash
docker compose exec web python manage.py migrate
```

---

## Docker Services

| Service | Description |
|----------|-------------|
| web | Django application served with Gunicorn |
| db | PostgreSQL database |
| redis | Redis cache and Redis Streams |

The Docker entrypoint automatically:

1. Applies database migrations.
2. Collects static files.
3. Starts Gunicorn.

---

# API Documentation

Swagger UI

```
http://127.0.0.1:8000/api/schema/swagger-ui/
```

OpenAPI Schema

```
http://127.0.0.1:8000/api/schema/
```

---

# Running Tests

Run the complete test suite

```bash
pytest
```

Run a module

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

| Module | Responsibility |
|----------|---------------|
| authentication | JWT authentication |
| customers | Customer management |
| transactions | Transaction CRUD and event publishing |
| rules | Compliance rule engine |
| alerts | Compliance alerts |
| audit | Audit trail |
| dashboard | Dashboard statistics |
| common | Shared models and utilities |
| worker | Redis Streams consumer |
| config | Django configuration |

---

# Architecture Overview

The application follows a layered architecture that separates API concerns from business logic and asynchronous processing.

```
                 Client
                    │
                    ▼
            Django REST API
                    │
                    ▼
          Serializer Validation
                    │
                    ▼
          Transaction Service
                    │
                    ▼
         Persist Transaction
                    │
                    ▼
       Publish Redis Stream Event
                    │
                    ▼
             Redis Streams
                    │
                    ▼
          Background Worker
                    │
                    ▼
             Rule Engine
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
     Alerts               Audit Logs
        │
        ▼
Customer Risk Classification
```

---

## Request Flow

1. Client submits a transaction.
2. The serializer validates the request.
3. The transaction is persisted.
4. A `transaction.created` event is published to Redis Streams.
5. The background worker consumes the event.
6. Registered compliance rules are evaluated.
7. A cumulative risk score is calculated.
8. Alerts are generated for triggered rules.
9. Audit logs are written.
10. Customers exceeding the configured threshold are automatically marked as high risk.

---

# Rule Engine

The compliance engine discovers registered rules dynamically at runtime.

Each rule returns:

- Whether it triggered
- Risk score contribution
- Severity
- Alert message

Example rules include:

- High transaction amount
- High-risk customer
- Transaction velocity
- Blacklisted country

Adding new rules only requires implementing the `Rule` interface—no changes to existing business logic are required.

---

# Design Decisions

## Service Layer

Business logic is separated from API views.

Benefits:

- Easier testing
- Reusable business logic
- Thin controllers
- Better maintainability

---

## Rule Engine

Rules are independent classes implementing a common interface.

Benefits:

- Open for extension
- Easy to test individually
- Supports plug-and-play rules
- Avoids large conditional statements

---

## Automatic Risk Classification

Customers cannot manually declare themselves high risk.

Risk status is determined entirely from transaction history and compliance rules.

Benefits:

- Prevents manipulation
- Ensures consistent compliance decisions
- Keeps business rules centralized

---

## Event-Driven Processing

Transaction creation publishes an event to Redis Streams.

A dedicated background worker processes events independently from the API request lifecycle.

Benefits:

- Reduced request latency
- Loose coupling
- Better scalability
- Easy future integration with notifications and analytics

---

## Audit Logging

Every compliance evaluation produces immutable audit records.

Benefits:

- Full traceability
- Compliance reporting
- Easier investigations

---

# Trade-offs

## Asynchronous Rule Evaluation

Compliance processing occurs after transaction creation.

Advantages

- Faster API responses
- Better scalability
- Easier background processing

Disadvantages

- Risk score and alerts are not immediately available after transaction creation.
- Additional infrastructure (Redis worker) is required.

---

## Threshold-Based Risk Classification

Customers become high risk once they exceed a configured score threshold.

Advantages

- Simple
- Predictable
- Easy to understand

Disadvantages

- Static thresholds may not adapt to evolving fraud patterns.

---

## Database-Centric Audit Trail

Alerts, risk scores and audit logs are persisted.

Advantages

- Historical reporting
- Compliance investigations
- Easy querying

Disadvantages

- Increased write operations

---

# Assumptions

The implementation assumes:

- Customer email addresses are unique.
- Every transaction belongs to exactly one customer.
- Transactions are immutable after completion except for administrative updates.
- Redis is available for event streaming.
- Authentication uses JWT access and refresh tokens.
- PostgreSQL is the production database.
- Compliance processing is eventually consistent due to asynchronous execution.
- High-risk classification is determined exclusively by backend business rules.

---

# Future Improvements

- Redis consumer groups for horizontal scaling
- Dead-letter queues and retry mechanisms
- Configurable compliance rules from the admin dashboard
- Rule weighting stored in the database
- Email and SMS notifications
- Alert assignment workflow
- Customer risk history
- Real-time dashboards using Server-Sent Events or WebSockets
- Machine learning–based fraud detection
- Multi-tenant support

---

# Development Commands

| Command | Description |
|----------|-------------|
| `python manage.py runserver` | Start development server |
| `python manage.py migrate` | Apply migrations |
| `python manage.py seed` | Seed sample customers and transactions |
| `python manage.py consumer` | Start Redis Streams worker |
| `python manage.py createsuperuser` | Create administrator |
| `python manage.py check` | Run Django system checks |
| `pytest` | Run all tests |
| `pytest transactions/tests.py` | Run transaction tests |
| `flake8 .` | Run linting |
