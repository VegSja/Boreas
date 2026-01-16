# Multi-stage build for Boreas Streamlit app
FROM python:3.13-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY dlt/requirements.txt dlt-requirements.txt
COPY dashboard/requirements.txt dashboard-requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r dlt-requirements.txt && \
    pip install --no-cache-dir -r dashboard-requirements.txt && \
    pip install --no-cache-dir dbt-duckdb streamlit

# Final stage
FROM python:3.13-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY dashboard /app/dashboard
COPY dlt /app/dlt
COPY src /app/src
COPY dbt_boreas /app/dbt_boreas

# Create non-root user
RUN useradd -m -u 1000 streamlit && \
    chown -R streamlit:streamlit /app

USER streamlit

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000', timeout=5)"

# Run Streamlit
EXPOSE 8000
CMD ["streamlit", "run", "dashboard/app.py", \
     "--server.port=8000", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--client.showErrorDetails=false"]
