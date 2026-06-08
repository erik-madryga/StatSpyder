# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy just the requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and their system dependencies.
# We do this before copying the rest of the app code so this heavy step is cached.
RUN playwright install chromium --with-deps

# Copy the rest of the backend application code
COPY . .

# Expose the port that the application listens on
EXPOSE 8000

# Start the application using Uvicorn. 
# Render passes the port via the $PORT environment variable.
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
