#!/bin/sh
# wait-for-fastapi.sh

set -e

host="$1"
shift
cmd="$@"

until nc -z "$host" 8001; do
  >&2 echo "FastAPI backend is unavailable - sleeping"
  sleep 1
done

>&2 echo "FastAPI backend is up - executing command"
exec $cmd
