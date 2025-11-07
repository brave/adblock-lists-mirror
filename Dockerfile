ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.9.4@sha256:c4089b0085cf4d38e38d5cdaa5e57752c1878a6f41f2e3a3a234dc5f23942cb4

# ----------------------------------
FROM ${UV_IMAGE} AS uv

FROM python:3.13-slim

WORKDIR /app

# Copy uv from the uv stage
COPY --from=uv /uv /usr/local/bin/

# Configure uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Copy project files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-cache

# Copy application code
COPY . .

CMD ["uv", "run", "python", "update-lists.py"]
