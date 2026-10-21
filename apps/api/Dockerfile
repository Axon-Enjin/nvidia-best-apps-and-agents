FROM python:3.14.5-slim-trixie@sha256:c845af9399020c7e562969a13689e929074a10fd057acd1b1fad06a2fb068e97
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_LINK_MODE=copy PATH=/app/.venv/bin:$PATH \
    NETWORK_MODE=offline AUTH_MODE=named AUTO_MIGRATE=false EMBEDDED_WORKER=false \
    SECRET_KEY_FILE=/data/account.key SOURCE_STORAGE_ROOT=/data/sources \
    OCR_BINARY=/usr/bin/tesseract OCR_EXPECTED_VERSION=5.5.0 TESSDATA_PREFIX=/opt/tessdata
RUN apt-get update && apt-get install -y --no-install-recommends tesseract-ocr=5.5.0-1+b1 postgresql-client-17 ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv==0.11.19 \
    && useradd --uid 10001 --create-home sentinel \
    && mkdir -p /data/sources /backups /opt/tessdata
RUN python -c "import urllib.request,hashlib,pathlib; b=urllib.request.urlopen('https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/4.1.0/eng.traineddata',timeout=60).read(); assert hashlib.sha256(b).hexdigest()=='7d4322bd2a7749724879683fc3912cb542f19906c83bcc1a52132556427170b2'; pathlib.Path('/opt/tessdata/eng.traineddata').write_bytes(b)"
WORKDIR /app
COPY apps/api/pyproject.toml apps/api/uv.lock ./
RUN uv sync --locked --no-dev --no-install-project
COPY apps/api/src ./src
COPY apps/api/migrations ./migrations
COPY apps/api/alembic.ini ./
COPY OCR-NOTICES.md LICENSE ./
# A wheel install, not an editable one: the image then runs the packaged static assets and migrations.
RUN uv sync --locked --no-dev --no-editable
RUN chown -R sentinel:sentinel /data /backups
USER 10001:10001
EXPOSE 8000
CMD ["python", "-m", "sentinel", "serve"]
