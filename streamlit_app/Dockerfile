FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    streamlit>=1.38 \
    duckdb>=1.4.3 \
    pandas>=2.3.3 \
    pydeck>=0.9 \
    altair>=5 \
    matplotlib>=3.9

COPY streamlit_app/ /app/streamlit_app/
COPY .streamlit/ /app/.streamlit/
RUN rm -f /app/streamlit_app/static/evidence

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app/Home.py", \
     "--server.address=0.0.0.0", "--server.port=8501", \
     "--server.headless=true", "--browser.gatherUsageStats=false"]
