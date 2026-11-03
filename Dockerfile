# syntax=docker/dockerfile:1
# Every line below is a layer. Docker caches layers so rebuilds stay fast
# if the files above the COPY that changed are unchanged.

FROM python:3.12-slim

# Metadata only — does not change how the image runs.
LABEL org.opencontainers.image.title="personal-task-board" \
      org.opencontainers.image.description="Practice Flask app for Docker learning"

# Container working directory. All later COPY/RUN/CMD paths are relative to this.
WORKDIR /app

# Install Python packages first, by themselves.
# That way editing app code does NOT force pip to run again.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the application source (see .dockerignore).
COPY app/ ./app/

# SQLite file will live here. Compose will mount a named volume on /data.
RUN mkdir -p /data && adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app /data

USER appuser

ENV PYTHONUNBUFFERED=1 \
    DATABASE_PATH=/data/tasks.db \
    PORT=8000

# Documents the port the process listens on. It does NOT publish it to your PC.
EXPOSE 8000

# Docker uses this to mark the container healthy/unhealthy.
HEALTHCHECK --interval=20s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

# gunicorn is a production WSGI server. 0.0.0.0 means "accept traffic from outside the container".
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app.main:app"]
