ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.11.27@sha256:4d01caf3b22dfd11003455e2e68153da08c4ee1fa54fdbd166c6282d22693419

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
