# Use lightweight official Python 3.11 slim image
FROM python:3.11-slim

# Set non-interactive + unbuffered output
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create non-root user
RUN adduser --system --group chakra

# Create app directory
WORKDIR /app

# Install system dependencies (e.g. for psycopg2 compilation if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements to a virtual environment
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Change ownership
RUN chown -R chakra:chakra /app

# Switch to non-root user
USER chakra

# Expose API port
EXPOSE 8000

# Run FastAPI app with Uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
