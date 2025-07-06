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

# Copy all app files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Expose port
EXPOSE 8000

# Start with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]