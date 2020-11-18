# Pull base image
FROM python:3.7-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /Disfactory

RUN apt-get update
RUN apt-get install -y binutils libproj-dev gdal-bin curl
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
RUN poetry config virtualenvs.create false

COPY . /Disfactory/

# Dev image
FROM base AS dev
RUN poetry install

# Prod image
FROM base AS prod
RUN poetry install --no-dev
