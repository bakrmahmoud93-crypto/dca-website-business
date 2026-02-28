FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p /data

# Expose port
EXPOSE 8000

# Set environment variable
ENV DATA_DIR=/data

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-", "backend.app:app"]
