#!/bin/bash
# End-to-end deploy-confidence test for the backend API.
#
# Boots the real prod image with the real prod entrypoint
# (scripts/start_prod.sh: wait-for-it -> collectstatic -> migrate ->
# gunicorn) against a throwaway PostGIS database, then asserts the
# HTTP API actually answers: stats, factory create round-trip, nearby
# query, and swagger wiring.
#
# Usage: ./scripts/e2e-api-test.sh
# Requires: Docker Engine + Compose (v2 plugin or v1 binary).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"
cd "$SCRIPT_DIR/.."

if docker compose version >/dev/null 2>&1; then
    COMPOSE="docker compose"
else
    COMPOSE="docker-compose"
fi

COMPOSE_FILE="docker-compose.test.yml"
SERVER_CONTAINER="disfactory-e2e-api"
BASE_URL="http://localhost:8000"

cleanup() {
    echo "Cleaning up..."
    docker rm -f "$SERVER_CONTAINER" >/dev/null 2>&1 || true
    # shellcheck disable=SC2086
    $COMPOSE -f "$COMPOSE_FILE" down -v --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "=== E2E: deploy-confidence test ==="

echo "1. Building prod image..."
# shellcheck disable=SC2086
$COMPOSE -f "$COMPOSE_FILE" build backend

echo "2. Starting throwaway PostGIS..."
# shellcheck disable=SC2086
$COMPOSE -f "$COMPOSE_FILE" up -d postgres
for _ in $(seq 1 30); do
    # shellcheck disable=SC2086
    if $COMPOSE -f "$COMPOSE_FILE" exec -T postgres pg_isready -U disfactory_user -d disfactory_test >/dev/null 2>&1; then
        break
    fi
    sleep 2
done

echo "3. Applying migrations (collectstatic + migrate)..."
# shellcheck disable=SC2086
$COMPOSE -f "$COMPOSE_FILE" run --rm backend bash -c "python manage.py collectstatic --noinput && python manage.py migrate"

echo "4. Booting API with the prod entrypoint (start_prod.sh)..."
# shellcheck disable=SC2086
$COMPOSE -f "$COMPOSE_FILE" run -d --name "$SERVER_CONTAINER" -p 8000:8000 backend ./scripts/start_prod.sh >/dev/null

echo "4. Waiting for API to answer..."
READY=0
for _ in $(seq 1 60); do
    if curl -sf -o /dev/null "$BASE_URL/api/statistics/total"; then
        READY=1
        break
    fi
    sleep 3
done
if [ "$READY" -ne 1 ]; then
    echo "API never became ready; server logs:"
    docker logs "$SERVER_CONTAINER" 2>&1 | tail -30
    exit 1
fi
echo "API is up."

echo "5. Asserting endpoints..."
check() {
    local desc="$1" expected="$2"
    shift 2
    local code
    code=$(curl -s -o /tmp/e2e-body -w "%{http_code}" "$@")
    if [ "$code" != "$expected" ]; then
        echo "FAIL: $desc: expected HTTP $expected, got $code"
        cat /tmp/e2e-body
        exit 1
    fi
    echo "ok: $desc -> $code"
}

check "GET /api/statistics/total" 200 "$BASE_URL/api/statistics/total"
check "GET /api/statistics/factories" 200 "$BASE_URL/api/statistics/factories"
check "GET /swagger/" 200 "$BASE_URL/swagger/"

check "POST /api/factories" 200 -X POST "$BASE_URL/api/factories" \
    -H "Content-Type: application/json" \
    -d '{"name":"e2e-smoke-factory","lat":23.5,"lng":121.0}'
grep -q "e2e-smoke-factory" /tmp/e2e-body || { echo "FAIL: created factory name not in response"; cat /tmp/e2e-body; exit 1; }
echo "ok: created factory echoed back"

check "GET /api/factories nearby" 200 "$BASE_URL/api/factories?lat=23.5&lng=121.0&range=1"
grep -q "e2e-smoke-factory" /tmp/e2e-body || { echo "FAIL: created factory not in nearby query"; cat /tmp/e2e-body; exit 1; }
echo "ok: nearby query returns the created factory"

echo
echo "E2E passed: image builds, prod entrypoint boots, migrations apply, API round-trips."
