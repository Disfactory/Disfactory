# Pull base image
FROM python:3.9 AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /Disfactory

RUN apt-get update
RUN apt-get install -y libproj-dev binutils curl

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
RUN uv sync --no-dev
COPY . /Disfactory/
ENV PATH="/Disfactory/.venv/bin:$PATH"
