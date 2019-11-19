#!/bin/sh
set -euo pipefail
PREFILL_DIR="prefill"

if [ "$1" = 'flask' ] || [ "$1" = "uwsgi" ]; then
	flask db upgrade
	if [ -d "$PREFILL_DIR" ]; then
		flask prefill "$PREFILL_DIR"
	fi
fi

exec "$@"
