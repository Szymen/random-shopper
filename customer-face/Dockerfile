FROM python:3.12 AS base
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY requirements.txt .
RUN uv pip install --system --no-cache-dir -r requirements.txt
COPY . .
# -------------------------------------------------------------------
FROM base AS test
RUN pytest tests/ -v
# -------------------------------------------------------------------
FROM base AS runtime
EXPOSE 5001
ENV PYTHONPATH=/app
ENV FLASK_APP=app:create_app
CMD ["python", "app.py"]
