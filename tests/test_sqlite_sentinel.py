DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3"
    },
}

SECRET_KEY = "django_tests_secret_key"
TIME_ZONE = "America/Chicago"
LANGUAGE_CODE = "en-us"
ADMIN_MEDIA_PREFIX = "/static/admin/"
STATICFILES_DIRS = ()

MIDDLEWARE_CLASSES = []

CACHES = {
    "default": {
        "BACKEND": "django_redis_sentinel.cache.RedisSentinelCache",
        "LOCATION": [
            ("sentinel1", 26379),
            ("sentinel2", 26379),
            ("sentinel3", 26379)
        ],
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis_sentinel.client.SentinelClient",
            "SENTINEL_SERVICE_NAME": "rmaster",
            "REDIS_CLIENT_KWARGS": {
                "db": 1
            }
        }
    },
    "without_sentinel": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis-master:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    },
    "without_sentinel_with_prefix": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis-master:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "test-prefix",
    },
    "doesnotexist": {
        "BACKEND": "django_redis_sentinel.cache.RedisSentinelCache",
        "LOCATION": [
            ("sentinel1", 26379),
            ("sentinel2", 26379),
            ("sentinel3", 26379)
        ],
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis_sentinel.client.SentinelClient",
            "SENTINEL_SERVICE_NAME": "rmaster",
            "REDIS_CLIENT_KWARGS": {
                "db": 1
            }
        }
    },
    "sample": {
        "BACKEND": "django_redis_sentinel.cache.RedisSentinelCache",
        "LOCATION": [
            ("sentinel1", 26379),
            ("sentinel2", 26379),
            ("sentinel3", 26379)
        ],
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis_sentinel.client.SentinelClient",
            "SENTINEL_SERVICE_NAME": "rmaster",
            "REDIS_CLIENT_KWARGS": {
                "db": 1
            }
        }
    },
    "with_prefix": {
        "BACKEND": "django_redis_sentinel.cache.RedisSentinelCache",
        "LOCATION": [
            ("sentinel1", 26379),
            ("sentinel2", 26379),
            ("sentinel3", 26379)
        ],
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis_sentinel.client.SentinelClient",
            "SENTINEL_SERVICE_NAME": "rmaster",
            "REDIS_CLIENT_KWARGS": {
                "db": 1
            }
        },
        "KEY_PREFIX": "test-prefix",
    },
}

INSTALLED_APPS = (
    "django.contrib.sessions",
    "redis_backend_testapp",
    "hashring_test",
)
