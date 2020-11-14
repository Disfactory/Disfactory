#!/bin/bash
SCRIPT_DIR="$( cd "$(dirname "$0")" ; pwd -P )"
ROOT_DIR="$SCRIPT_DIR/.."
SOURCE_FILE=${ROOT_DIR}/.env

# Go to root folder
cd $ROOT_DIR

# Load environment variables
if [ ! -f "$SOURCE_FILE" ]; then
    echo "$SOURCE_FILE does not exist."
    exit 1
fi
source $ROOT_DIR/.env

echo "Waiting postgreSQL ${DISFACTORY_BACKEND_DEFAULT_DB_HOST}:${DISFACTORY_BACKEND_DEFAULT_DB_PORT}"
$ROOT_DIR/scripts/wait-for-it.sh ${DISFACTORY_BACKEND_DEFAULT_DB_HOST}:${DISFACTORY_BACKEND_DEFAULT_DB_PORT} -- bash -c "python manage.py migrate;python manage.py qcluster"
