FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PVE_DIAG_BIND=0.0.0.0 \
    PVE_DIAG_PORT=8765 \
    PVE_DIAG_TRUSTED_PROXY=1 \
    PVE_DIAG_WEB_ROOT=/app/site \
    PVE_DIAG_ENV_FILE=/run/secrets/connector.env

WORKDIR /app

RUN groupadd --system --gid 10001 pve-diagnostic \
    && useradd --system --uid 10001 --gid pve-diagnostic \
       --no-create-home --home-dir /nonexistent --shell /usr/sbin/nologin pve-diagnostic \
    && mkdir -p /app/site/prototype /app/site/docs

COPY --chown=root:root prototype/server.py /app/server.py
COPY --chown=root:root prototype/index.html /app/site/prototype/index.html
COPY --chown=root:root docs/index.html /app/site/index.html
COPY --chown=root:root docs/ /app/site/docs/
COPY --chown=root:root README.md /app/site/README.md

USER 10001:10001
EXPOSE 8765

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["python", "-c", "from urllib.request import urlopen; urlopen('http://127.0.0.1:8765/healthz', timeout=2).read()"]

CMD ["python", "/app/server.py"]
