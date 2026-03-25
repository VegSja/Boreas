FROM python:3.12-slim

# Install uv
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY README.md .
COPY dashboard/ ./dashboard/
COPY src/ ./src/
COPY .streamlit/ ./.streamlit/   # theme config (light theme, custom colours)

# Install all dependencies including dashboard extras
RUN uv pip install --system ".[dashboard]"

# Expose Streamlit port
EXPOSE 8501

# The database is expected to be mounted at /app/boreas.duckdb
ENV BOREAS_DB_PATH=/app/boreas.duckdb

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

CMD ["python", "-m", "streamlit", "run", "dashboard/app.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501", \
     "--server.headless=true"]
