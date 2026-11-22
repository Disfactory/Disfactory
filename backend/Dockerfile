# Pull base image
FROM python:3.12 AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /Disfactory

# update + install in one layer so a cached, stale package index can't break the install.
# (GeoDjango libs libproj-dev/binutils dropped: the app uses the plain postgresql backend.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
COPY pyproject.toml uv.lock ./

# Dev image
FROM base AS dev
RUN uv sync --dev
COPY . /Disfactory/
ENV PATH="/Disfactory/.venv/bin:$PATH"

# Prod image
FROM base AS prod
RUN uv sync --locked --no-dev
# Dependencies are baked in; stop `uv run` in start scripts from re-syncing (and pulling the dev group) at boot
ENV UV_NO_SYNC=1
COPY . /Disfactory/
ENV PATH="/Disfactory/.venv/bin:$PATH"
