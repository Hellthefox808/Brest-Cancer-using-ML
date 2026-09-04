# Multi-stage lightweight Python container
FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    HOST=0.0.0.0

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Run ML pipeline to ensure latest artifacts are generated inside image
RUN python -m pipeline.run_pipeline

# Expose server port
EXPOSE 5000

# Run Flask backend with Gunicorn WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "backend.app:create_app()"]
