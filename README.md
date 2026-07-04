# SmartComply Backend

SmartComply is a transaction monitoring and risk assessment platform designed to identify and flag potentially fraudulent or high-risk financial transactions based on configurable rules.

## Features

- **Transaction Processing**: Core support for various transaction types including deposits, withdrawals, and transfers.
- **Rule Engine**: A robust engine that evaluates each transaction against multiple criteria such as:
    - Transaction amount limits.
    - Customer risk profiles (e.g., `is_high_risk`).
    - Velocity checks (transaction frequency).
    - Blacklisted countries/regions.
- **Risk Scoring**: Every transaction is evaluated and assigned a risk score based on triggered rules.
- **Alerting & Auditing**: Automatic alerting for high-risk activities and comprehensive audit logging of all system actions.
- **Robust Authentication**: Secure integration with JWT (JSON Web Tokens) for authentication and authorization.
- **Comprehensive API Documentation**: Automatically generated OpenAPI documentation using `drf-spectacular`.

## Tech Stack

- **Framework**: [Django](https://www.djangoproject.com/)
- **API**: [Django REST Framework](https://www.django-rest-framework.org/)
- **Authentication**: [Simple JWT](https://github.com/dj-auth/dj-rest-schema)
- **Database**: PostgreSQL
- **Caching & Message Broker**: Redis
- **Documentation**: DRF Spectacular (OpenAPI 3)
- **Testing**: Pytest, FactoryBoy
- **Server**: Gunicorn

## Getting Started

### Prerequisites

Ensure you have the following installed:
- Python 3.10+
- PostgreSQL
- Redis

### Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd backend
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration**:
    Create a `.env` file in the `backend` directory and add the following configuration:

    ```env
    SECRET_KEY=your_secret_key_here
    DEBUG=True
    ALLOWED_HOSTS=*
    
    # Database Configuration
    DB_NAME=smartcomply_db
    DB_USER=your_user
    DB_PASSWORD=your_password
    DB_HOST=localhost
    DB_PORT=5432

    # Redis Configuration
    REDIS_HOST=localhost
    REDIS_PORT=6379
    ```

### Running the Application

1.  **Apply Migrations**:
    ```bash
    python manage.py migrate
    ```

2.  **Create a Superuser**:
    ```bash
    python manage.py createsuperuser
    ```

3.  **Run the Development Server**:
    ```bash
    python manage.py runserver
    ```
    The API will be available at `http://127.0.0.1:8000/`.

4.  **API Documentation**:
    View the interactive Swagger UI documentation at `http://127.0.0.1:8000/api/schema/swagger-ui/`.

## Project Structure

- `transactions`: Handles the core transaction lifecycle and logic.
- `rules`: Contains the rules engine and individual rule definitions (e.g., high amount, velocity).
- `customers`: Manages customer profiles and risk flags.
- `alerts`: Handles system alerts for flagged transactions.
- `audit`: Provides audit logging for security and compliance.
- `authentication`: Handles user authentication and permissions.
- `common`: Contains shared models and utilities.
- `worker`: Background processing tasks (e.g., rule evaluations, notification dispatching).
- `config`: Global application configuration and settings.

## Testing

To run the test suite:
```bash
python manage.py test
# Or using pytest directly
pytest
```

## Development Commands

| Command | Description |
| --- | --- |
| `python manage.py migrate` | Applies database migrations |
| `python manage.py createsuperuser` | Creates an admin user |
| `python manage.py runserver` | Starts the local development server |
| `pytest` | Runs all unit and integration tests |
