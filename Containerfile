FROM ghcr.io/astral-sh/uv:python3.14-alpine AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM python:3.14-alpine
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY app ./app
ENV PATH="/app/.venv/bin:$PATH" PORT=8000
CMD ["sh", "-c", "fastapi run app/main.py --host 0.0.0.0 --port $PORT"]
