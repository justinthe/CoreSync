# CHANGE THIS LINE: Use the stable Bookworm release
FROM python:3.11-slim-bookworm

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Ensure output is sent directly to terminal (logs)
ENV PYTHONUNBUFFERED=1

# Set work directory inside the container
WORKDIR /code

# Install system dependencies
# We add --no-install-recommends to keep it small and clean
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /code/