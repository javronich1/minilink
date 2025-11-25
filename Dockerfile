# Use a small Python base image
FROM python:3.11-slim

# Do not write .pyc files and flush stdout/stderr immediately
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Install system dependencies (for SQLite etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# 1) Copy only requirements first (better for Docker layer caching)
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 2) Now copy the actual application code
COPY app ./app
COPY tests ./tests

# Expose the application port (Azure expects 80)
EXPOSE 80

# Default command: run uvicorn on port 80
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]