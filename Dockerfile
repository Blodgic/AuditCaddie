FROM python:3.12-slim

LABEL org.opencontainers.image.title="AuditCaddie OSS"
LABEL org.opencontainers.image.description="Self-hosted compliance scanning for AWS and GitHub"
LABEL org.opencontainers.image.source="https://github.com/Blodgic/AuditCaddie"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Data volume (SQLite + reports)
RUN mkdir -p /data
VOLUME ["/data"]

ENV DATA_DIR=/data \
    PORT=8080 \
    PYTHONUNBUFFERED=1

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/api/health')"

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
