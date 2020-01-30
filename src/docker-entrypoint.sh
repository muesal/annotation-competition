#!/bin/sh
set -euo pipefail
PREFILL_DIR="prefill"

if [ "$1" = 'flask' ] || [ "$1" = "uwsgi" ]; then
	# The flask initialisation is currently broken without any data
	flask nltk-data || python -m nltk.downloader -d ${NLTK_DATA:=/usr/share/nltk_data} all
	flask db upgrade
	if [ -d "$PREFILL_DIR" ]; then
		flask prefill "$PREFILL_DIR"
	fi
fi

exec "$@"
