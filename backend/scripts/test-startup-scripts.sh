#!/bin/bash
# Simple test for the startup scripts without requiring full docker setup

set -e

SCRIPT_DIR="$( cd "$(dirname "$0")" ; pwd -P )"
cd "$SCRIPT_DIR/.."

echo "Testing startup script syntax..."

# Test that the scripts have proper syntax
echo "✓ Testing start_prod.sh syntax..."
bash -n scripts/start_prod.sh

echo "✓ Testing start_worker.sh syntax..."
bash -n scripts/start_worker.sh

echo "✓ Testing start.sh syntax..."
bash -n scripts/start.sh

echo "✓ Testing wait-for-migrations.sh syntax..."
bash -n scripts/wait-for-migrations.sh

echo "✓ All startup scripts have valid syntax!"

# Test that the static directory exists
if [ -d "static" ]; then
    echo "✓ Static directory exists"
else
    echo "❌ Static directory missing"
    exit 1
fi

# Test that wait-for-migrations script is executable
if [ -x "scripts/wait-for-migrations.sh" ]; then
    echo "✓ wait-for-migrations.sh is executable"
else
    echo "❌ wait-for-migrations.sh is not executable"
    exit 1
fi

echo "✅ All basic tests passed!"