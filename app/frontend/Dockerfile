FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    portaudio19-dev \
    python3-pyaudio \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
# to save time
COPY . .

# Use the PORT environment variable provided by Cloud Run
ENV PORT 8000

# Expose the port
EXPOSE ${PORT}

# Run the Streamlit app with the PORT environment variable
CMD streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0