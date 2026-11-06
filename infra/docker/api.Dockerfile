# Topiome API + worker image. Build from the repository root:
#   docker build -f infra/docker/api.Dockerfile -t topiome-api .
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH=/opt/venv/bin:$PATH

# Same uv as development, so uv.lock is read identically.
RUN pip install --no-cache-dir uv==0.12.5

WORKDIR /app
# The source disk (exFAT) can carry 0700 modes, so every copy is chowned to the
# runtime user; otherwise `USER topiome` cannot even read the app package.
RUN useradd --create-home --uid 10001 topiome \
    && mkdir -p /data/storage \
    && chown topiome /data/storage

# Dependencies first so code changes do not invalidate the layer.
COPY --chown=topiome:topiome packages/analysis /app/packages/analysis
COPY --chown=topiome:topiome apps/api/pyproject.toml apps/api/uv.lock /app/apps/api/
WORKDIR /app/apps/api
RUN uv sync --frozen --no-dev --no-install-project

COPY --chown=topiome:topiome packages/disease-packs /app/packages/disease-packs
COPY --chown=topiome:topiome apps/api /app/apps/api
USER topiome

ENV APP_ENV=production \
    QUEUE_MODE=worker \
    STORAGE_DIR=/data/storage \
    AUTO_SEED=false \
    ALLOW_DEMO_LOGIN=false

EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=5 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health', timeout=4).status == 200 else 1)"

# Only the web container can reach the API (internal network), so forwarded
# client addresses from the Next.js proxy are trusted for audit logs and throttling.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers", "--forwarded-allow-ips", "*"]
