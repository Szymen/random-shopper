FROM python:3.12 AS base
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY requirements.txt .
RUN uv pip install --system --no-cache-dir -r requirements.txt
# -------------------------------------------------------------------
FROM base AS test
COPY . .
RUN pytest tests/ -v
# -------------------------------------------------------------------
FROM base AS runtime

# Run as non-root (Kubernetes also sets runAsNonRoot=true).
ARG UID=10001
ARG GID=10001
RUN groupadd -g ${GID} app && useradd -m -u ${UID} -g ${GID} -s /usr/sbin/nologin app

COPY --chown=app:app . .

EXPOSE 5001
ENV PYTHONPATH=/app
ENV FLASK_APP=app:create_app

RUN chmod 0755 /app/entrypoint.sh

USER app
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "app.py"]
