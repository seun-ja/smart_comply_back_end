# Build stage
FROM python:3.12-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_COMPILE=on

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    libc-dev \
    && rm -rf /var/lib/apt/lists/*

# Install requirements
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# Runtime stage
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install runtime dependencies (needed for psycopg)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy project files
COPY . .

# Setup entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose port 8000
EXPOSE 8000

# Entrypoint for automatic migrations and static collection
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
