# Use a slim official Python image
FROM python:3.12-slim

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install OS-level dependencies for PostgreSQL
RUN apt-get update && \
    apt-get install -y gcc g++ curl libpq-dev build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy all app files
COPY . .

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    mkdir -p reqmod/logging_storage && \
    chown -R app:app /app && \
    chmod -R 755 /app
USER app

# Expose port
EXPOSE 8000

# Start with gunicorn - use PORT env var if available, default to 8000
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 120 --access-logfile - --error-logfile - wsgi:application"]