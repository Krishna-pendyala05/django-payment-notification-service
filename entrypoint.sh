#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to wait for a service to be ready
wait_for_service() {
    local host="$1"
    local port="$2"
    echo "Waiting for $host:$port..."
    while ! nc -z "$host" "$port"; do
      sleep 1
    done
    echo "$host:$port is ready!"
}

# Wait for database if DATABASE_URL is set and points to a host
if [[ "$DATABASE_URL" == *"postgres"* ]]; then
    # Extract host and port from DATABASE_URL if possible, or use defaults
    # This is a simple check, in production you'd use a more robust way
    DB_HOST=$(echo $DATABASE_URL | sed -e 's/.*@//' -e 's/:.*//' -e 's/\/.*//')
    DB_PORT=$(echo $DATABASE_URL | sed -e 's/.*://' -e 's/\/.*//')
    wait_for_service "${DB_HOST:-db}" "${DB_PORT:-5432}"
fi

# Apply database migrations
if [ "$SKIP_MIGRATIONS" != "true" ]; then
    echo "Applying database migrations..."
    python manage.py migrate --noinput
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Execute the CMD from Dockerfile
exec "$@"
