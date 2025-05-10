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

# Set environment variables for local development
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV USE_MOCK_RESPONSES=true
ENV ENVIRONMENT=local

# Expose the port
EXPOSE ${PORT}

# Run the API server
CMD ["python", "-u", "main.py"]