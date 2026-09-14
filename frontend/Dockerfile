FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=180 -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK --interval=10s --timeout=5s --retries=8 --start-period=20s \
    CMD curl -fsS http://127.0.0.1:8501/_stcore/health >/dev/null || exit 1

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--browser.gatherUsageStats=false"]
