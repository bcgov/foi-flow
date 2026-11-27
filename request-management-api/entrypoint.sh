#!/bin/sh
set -e

if [ "$#" -gt 1 ]; then
    echo "Usage: entrypoint.sh [serve|migrate]" >&2
    exit 2
fi

case "${1-serve}" in
    serve)
        exec python wsgi.py
        ;;
    migrate)
        exec python manage.py db upgrade
        ;;
    *)
        echo "Usage: entrypoint.sh [serve|migrate]" >&2
        exit 2
        ;;
esac
