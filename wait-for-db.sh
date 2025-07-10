#!/bin/sh
set -e

host="$1"
shift

until pg_isready -h "$(echo "$host" | cut -d: -f1)" -p "$(echo "$host" | cut -d: -f2)" > /dev/null 2>&1; do
  echo "Waiting for PostgreSQL at $host..."
  sleep 1
done

echo "PostgreSQL is ready - starting app"
exec "$@"
