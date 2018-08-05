FROM python:3.6-alpine

MAINTAINER danigosa <danigosa@gmail.com>

RUN apk add --no-cache --virtual .build-deps \
            gcc \
            make \
            libc-dev \
            musl-dev \
            linux-headers \
    && python -m venv /venv \
    && /venv/bin/pip install -U pip \
    && /venv/bin/pip install --no-cache-dir -U django-redis==4.9.0 'Django>=2.0.0,<2.1.0' hiredis mock msgpack-python fakeredis \
    && runDeps="$( \
        scanelf --needed --nobanner --recursive /venv \
        | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
        | sort -u \
        | xargs -r apk info --installed \
        | sort -u \
        )" \
    && apk add --virtual .python-rundeps $runDeps bash \
    && apk del .build-deps

RUN mkdir /django-redis-sentinel

COPY . /django-redis-sentinel
WORKDIR /django-redis-sentinel
VOLUME /django-redis-sentinel
COPY entrypoint.sh /


ENTRYPOINT ["/entrypoint.sh"]
