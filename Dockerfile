ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.13.6@sha256:af22a52f5eafef3d78e551599d405c02df61919d18028f0cea8eda93bc9986d0

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
