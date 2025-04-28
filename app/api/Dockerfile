FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create directory for models if it doesn't exist
RUN mkdir -p /data/models

# Use the PORT environment variable provided by Cloud Run
ENV PORT 8080

# Expose the port
EXPOSE ${PORT}

# Run the API server with the PORT environment variable
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}