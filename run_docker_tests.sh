#!/usr/bin/env bash
set -e
#DJANGO_REDIS_CONTAINER=`docker ps -aqf "name=django-redis-sentinel"`
#docker exec -t $DJANGO_REDIS_CONTAINER bash /django-redis/tests/run_sentinel_tests.sh
docker-compose exec django-redis /bin/bash /django-redis-sentinel/tests/run_sentinel_tests.sh
