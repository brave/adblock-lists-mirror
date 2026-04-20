ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.11.7@sha256:240fb85ab0f263ef12f492d8476aa3a2e4e1e333f7d67fbdd923d00a506a516a

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
