#!/usr/bin/sh

set -e

# 1. Get the CPU count
# If nproc is unavailable, it defaults to 1
CPUS=$(nproc --all || echo 1)

# 2. Calculate WORKER_COUNT: (CPU * 2) + 1
#WORKER_COUNT=$(( (CPUS * 2) + 1 ))
WORKER_COUNT=1

echo "Detected ${CPUS} CPUs. Setting WORKER_COUNT to ${WORKER_COUNT}."

python manage.py migrate --settings=$DJANGO_SETTINGS_MODULE

# core count for captor admin web server is 2 (best practice core count + 1)
gunicorn battlefield.wsgi --workers="${WORKER_COUNT}" --preload -b 0.0.0.0:"${PORT}" --access-logfile=- --error-logfile=-