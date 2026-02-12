ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.9.28@sha256:59240a65d6b57e6c507429b45f01b8f2c7c0bbeee0fb697c41a39c6a8e3a4cfb

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
