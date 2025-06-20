#!/bin/bash
# Test script for docker-compose service initialization

set -e

SCRIPT_DIR="$( cd "$(dirname "$0")" ; pwd -P )"
cd "$SCRIPT_DIR"

echo "Starting Docker Compose test..."

# Clean up any existing containers
docker-compose -f docker-compose.test.yml down -v --remove-orphans || true

# Build and run the test
echo "Building and starting services..."
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from worker

# Check exit codes
BACKEND_EXIT=$(docker-compose -f docker-compose.test.yml ps -q backend | xargs docker inspect --format='{{.State.ExitCode}}')
WORKER_EXIT=$(docker-compose -f docker-compose.test.yml ps -q worker | xargs docker inspect --format='{{.State.ExitCode}}')

echo "Backend exit code: $BACKEND_EXIT"
echo "Worker exit code: $WORKER_EXIT"

# Clean up
docker-compose -f docker-compose.test.yml down -v --remove-orphans

if [ "$BACKEND_EXIT" -eq 0 ] && [ "$WORKER_EXIT" -eq 0 ]; then
    echo "✅ Docker Compose test passed!"
    exit 0
else
    echo "❌ Docker Compose test failed!"
    exit 1
fi