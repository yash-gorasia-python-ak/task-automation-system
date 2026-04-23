#!/bin/bash
set -e

echo "Running Database Migrations..."
# Run alembic migrations
uv run alembic upgrade head


if [ -n "$1" ]; then
    exec "$@"
fi
