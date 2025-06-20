# Docker Service Initialization Fixes

This document summarizes the fixes applied to resolve the docker-compose service initialization issues reported in #667.

## Issues Identified

### 1. Static Files Collection Error
**Error:** `FileNotFoundError: [Errno 2] No such file or directory: '/Disfactory/static'`

**Root Cause:** 
- The `static` directory didn't exist in the Docker image
- Django's `STATIC_ROOT` setting was not configured
- `collectstatic` command failed during container startup

**Fix:**
- Created `/backend/static/` directory with `.gitkeep` file
- Added `STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")` to settings.py
- Updated `.gitignore` to allow the `.gitkeep` file

### 2. Django-Q Worker Database Error
**Error:** `django.db.utils.ProgrammingError: relation "django_q_ormq" does not exist`

**Root Cause:**
- Worker service started before database migrations were completed
- Django-Q tables didn't exist when qcluster tried to access them

**Fix:**
- Created `wait-for-migrations.sh` script to check for completed migrations
- Updated `start_worker.sh` to wait for migrations before starting qcluster
- Ensured proper service startup order

## Changes Made

### New Files
- `backend/static/.gitkeep` - Ensures static directory exists
- `backend/scripts/wait-for-migrations.sh` - Waits for migrations to complete
- `backend/scripts/test-startup-scripts.sh` - Tests script validity
- `backend/scripts/integration-test.sh` - Comprehensive integration test
- `backend/docker-compose.test.yml` - Test configuration

### Modified Files
- `backend/gis_project/settings.py` - Added STATIC_ROOT configuration
- `backend/scripts/start_prod.sh` - Added collectstatic and migrate steps
- `backend/scripts/start.sh` - Added collectstatic step for consistency
- `backend/scripts/start_worker.sh` - Added migration waiting
- `backend/.gitignore` - Allow static/.gitkeep file
- `.github/workflows/tests.yml` - Added startup script tests

## Testing

### Integration Tests
Run the comprehensive integration test:
```bash
cd backend
./scripts/integration-test.sh
```

### Startup Script Tests
Test script syntax and requirements:
```bash
cd backend
./scripts/test-startup-scripts.sh
```

### Manual Verification
Test collectstatic command:
```bash
docker run --rm -e DISFACTORY_ALLOWED_HOST="*" <image> \
  bash -c "cd /Disfactory && python manage.py collectstatic --dry-run --noinput"
```

## For Users

The original docker-compose.yml from the issue should now work correctly with images built from the updated code. The key improvements:

1. **Static files**: `collectstatic` command will now succeed
2. **Service startup**: Worker will wait for backend to complete migrations
3. **Error handling**: Better logging and error messages during startup

### Recommended Docker Compose Configuration

For production use, ensure your docker-compose.yml includes:

```yaml
services:
  backend:
    command: >
      sh -c "
        cd /Disfactory &&
        python manage.py collectstatic --noinput &&
        python manage.py migrate &&
        gunicorn -c gunicorn.conf.py gis_project.wsgi
      "
    # ... other backend config

  worker:
    depends_on:
      postgres:
        condition: service_healthy
      backend:
        condition: service_completed_successfully  # Important!
    command: >
      sh -c "
        cd /Disfactory &&
        python manage.py qcluster
      "
    # ... other worker config
```

The fixes ensure that:
- Static files are properly collected before the server starts
- Database migrations run before any Django application starts
- Workers wait for the backend setup to complete before starting