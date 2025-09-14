## ------------------------------- Builder Stage ------------------------------ ##
FROM python:3.13-bookworm AS builder

RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential curl libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Download the latest installer, install it and then remove it
ADD https://astral.sh/uv/install.sh /install.sh
RUN chmod -R 655 /install.sh && /install.sh && rm /install.sh

# Set up the UV environment path correctly
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY ./pyproject.toml .

RUN uv sync

## ------------------------------- Production Stage ------------------------------ ##
FROM python:3.13-slim-bookworm AS production

WORKDIR /app

COPY . .
COPY --from=builder /app/.venv .venv

# Set up environment variables for production
ENV PATH="/app/.venv/bin:$PATH"

# Expose the specified port for FastAPI
ENV PORT=8000
EXPOSE $PORT

# Start
CMD ["/bin/sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
