# Pull base image
FROM python:3.7-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /Disfactory

RUN apt-get update
RUN apt-get install -y binutils libproj-dev gdal-bin
RUN pip install pipenv

COPY . /Disfactory/

# Dev image
FROM base AS dev
RUN pipenv install --dev --system

# Prod image
FROM base AS prod
RUN pipenv install --system
