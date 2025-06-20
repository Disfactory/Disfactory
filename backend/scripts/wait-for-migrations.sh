#!/bin/bash
# wait-for-migrations.sh - Wait for Django migrations to complete
# Usage: wait-for-migrations.sh [max_wait_seconds]

MAX_WAIT=${1:-300}  # Default 5 minutes
WAIT_INTERVAL=5
ELAPSED=0

echo "Waiting for Django migrations to complete..."

while [ $ELAPSED -lt $MAX_WAIT ]; do
    # Check if we can query the django_migrations table
    if python manage.py showmigrations --plan >/dev/null 2>&1; then
        echo "Migrations table is accessible, checking for pending migrations..."
        
        # Check if there are any unapplied migrations
        if python manage.py showmigrations --plan | grep -q "\[ \]"; then
            echo "Found pending migrations, waiting..."
        else
            echo "All migrations are applied!"
            exit 0
        fi
    else
        echo "Cannot access migrations table yet, waiting..."
    fi
    
    sleep $WAIT_INTERVAL
    ELAPSED=$((ELAPSED + WAIT_INTERVAL))
    echo "Waited ${ELAPSED}s/${MAX_WAIT}s..."
done

echo "Timeout waiting for migrations to complete"
exit 1