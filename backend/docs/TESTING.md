# Testing

This document describes how to run tests for the Disfactory backend.

## Prerequisites

- Docker Engine >= 18.06.0
- Docker Compose

## Running Tests with Docker Compose (Recommended)

The recommended way to run tests is using Docker Compose with the development configuration.

### Start the Development Environment

First, make sure the development containers are running:

```bash
docker compose -f docker-compose.dev.yml up -d
```

### Run All Tests

Using Make:

```bash
make test
```

Or directly with Docker Compose:

```bash
docker compose -f docker-compose.dev.yml exec web pytest -vv
```

### Run Specific Test Files

To run tests for a specific module:

```bash
docker compose -f docker-compose.dev.yml run --rm web pytest api/views/tests/test_image_upload.py -v
```

### Run Tests Matching a Pattern

To run tests matching a specific name pattern:

```bash
docker compose -f docker-compose.dev.yml run --rm web pytest -k "test_upload" -v
```

## Test Configuration

The test configuration is defined in `pytest.ini`:

```ini
[pytest]
addopts = -k 'not deprecated'
DJANGO_SETTINGS_MODULE = gis_project.settings
env_files = .env
```

- Tests marked as `deprecated` are excluded by default
- Django settings are loaded from `gis_project.settings`
- Environment variables are loaded from `.env` file

## Environment Variables for Testing

The `.env.test` file contains environment variables specific to testing. Key variables include:

| Variable | Description | Example |
|----------|-------------|---------|
| `DISFACTORY_BACKEND_DEFAULT_DB_NAME` | Test database name | `disfactory_data` |
| `DISFACTORY_BACKEND_DEFAULT_DB_HOST` | Database host | `db` |
| `DISFACTORY_BACKEND_MEDIA_ROOT` | Media files directory | `./images/` |
| `DISFACTORY_MEDIA_DIR` | Docker volume for media | `/tmp/disfactory/media` |

## Writing Tests

### Test Location

Tests are located in `tests/` subdirectories within each module:

```
api/
  views/
    tests/
      __init__.py
      test_factories_cr.py
      test_image_upload.py
      ...
  models/
    tests/
      __init__.py
      test_factory.py
      ...
```

### Test Fixtures

Common pytest fixtures are defined in `conftest.py`. Django-specific fixtures (like `client`, `settings`) are provided by `pytest-django`.

### Example Test

```python
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
def test_example(client, settings):
    """Example test with database access."""
    # Modify settings for this test
    settings.SOME_SETTING = "test_value"
    
    # Make a request
    response = client.get("/api/endpoint")
    
    # Assert the response
    assert response.status_code == 200
```

## Troubleshooting

### Port Already Allocated

If you see an error like:

```
Bind for 0.0.0.0:5433 failed: port is already allocated
```

Stop any existing containers using that port:

```bash
docker compose -f docker-compose.dev.yml down
# Or stop specific containers
docker stop <container_name>
```

### Database Not Ready

If tests fail with database connection errors, ensure the database container is healthy:

```bash
docker compose -f docker-compose.dev.yml ps
```

Wait for the `db` service to show as "healthy" before running tests.

### Apps Not Loaded

If you see `AppRegistryNotReady: Apps aren't loaded yet`, make sure you're running tests through Docker Compose which properly initializes Django:

```bash
# Correct way
docker compose -f docker-compose.dev.yml run --rm web pytest

# This may fail outside Docker
pytest  # Don't run directly without proper Django setup
```
