FROM python:3.8-alpine

WORKDIR /tmp
COPY requirements.txt requirements.txt

RUN set -eux; \
	apk add --no-cache --virtual .build-deps\
		gcc \
		libffi-dev \
		linux-headers \
		musl-dev \
		mariadb-connector-c-dev \
		postgresql-dev \
	; \
	pip install --no-cache-dir -r requirements.txt; \
	\
	runDeps="$( \
		scanelf --needed --nobanner --format '%n#p' --recursive /usr/local/lib/python3.8 \
			| tr ',' '\n' \
			| sort -u \
			| awk 'system("[ -e /usr/local/lib/" $1 " ]") == 0 { next } { print "so:" $1 }' \
		)"; \
	apk add --virtual .app-rundeps $runDeps; \
	apk del .build-deps

WORKDIR /app

EXPOSE 5000

COPY docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["flask", "run", "-h", "0.0.0.0"]
#CMD ["uwsgi", "-w", "app:app", "--socket", "0.0.0.0:5000"]
