# -*- coding: utf-8 -*-
import socket

try:
    import consulate
except ImportError:
    consulate = None

from django.core.cache.backends.base import DEFAULT_TIMEOUT, get_key_func
from django.core.exceptions import ImproperlyConfigured
from redis.exceptions import ConnectionError, ResponseError, TimeoutError
from django_redis.exceptions import ConnectionInterrupted
from django_redis.client.default import DefaultClient
from django_redis.util import load_class
from django_redis_sentinel import pool

_main_exceptions = (TimeoutError, ResponseError, ConnectionError, socket.timeout)


class SentinelClient(DefaultClient):
    """
    Modifies DefaultClient to work on Sentinel Cluster. URLs passed as servers are no longer master on index 0 and
    slaves the following ones. All URLs should represent the list of sentinels, where order no matters anymore.
    It does not use any cached ConnectionPool as SentinelConnectionPool is for sentinels, not master and slaves.
    The Sentinel client creates a StrictRedis client that performs the connections to actual current elected master or
    slave instances, instead of indexing the URLs for using them as a fixed way to connect to each server.
    This way, through Sentinel client instead of direct creation of StrictRedis from URLs,
    we always have a valid master or slave client (before or after failover).
    New OPTIONS:
        - SENTINEL_SERVICE_NAME (required): Name of monitored cluster
        - SENTINEL_SOCKET_TIMEOUT (optional): Socket timeout for connecting to sentinels, in seconds (accepts float)
    """

    def __init__(self, server, params, backend):
        self._backend = backend
        self._server = server
        self._params = params

        self.reverse_key = get_key_func(params.get("REVERSE_KEY_FUNCTION") or
                                        "django_redis.util.default_reverse_key")

        self._options = params.get("OPTIONS", {})

        if self._options.get('USE_CONSUL', False) and consulate is not None:
            sentinel_port = self._options.get('SENTINEL_PORT', '26379')
            consul = consulate.Consul(host=self._options.get('CONSUL_IP_ADDR', 'localhost'))
            self._server = [
                (node['Address'], sentinel_port) for node in consul.catalog.nodes() 
                if node['Meta'].get('consul_role') == 'server'
            ]
        if not self._server:
            raise ImproperlyConfigured("Missing connections string")

        if not isinstance(self._server, (list, tuple, set)):
            self._server = self._server.split(",")

        # In Redis Sentinel (not Redis Cluster) all slaves in read-only mode
        self._slave_read_only = True

        serializer_path = self._options.get("SERIALIZER", "django_redis.serializers.pickle.PickleSerializer")
        serializer_cls = load_class(serializer_path)

        compressor_path = self._options.get("COMPRESSOR", "django_redis.compressors.identity.IdentityCompressor")
        compressor_cls = load_class(compressor_path)

        self._serializer = serializer_cls(options=self._options)
        self._compressor = compressor_cls(options=self._options)

        # Hack: Add sentinels servers as options, to break legacy pool code as less as possible
        self._options.update({"SENTINELS": self._server})
        # Create connection factory for Sentinels
        self.connection_factory = pool.get_connection_factory(options=self._options)

    def get_client(self, write=True, force_slave=False):
        """
        Method used for obtain a raw redis client.

        This function is used by almost all cache backend
        operations for obtain a native redis client/connection
        instance.

        If read always looks for a slave (round-robin algorithm, with fallback to master if none available)
        If write then it looks for master
        """
        if write:
            return self.connect(master=True)
        else:
            return self.connect(master=False, force_slave=force_slave)

    def connect(self, master=True, force_slave=False):
        """
        Given a type of connection master or no master, returns a new raw redis client/connection
        instance. Sentinel always give a valid StrictRedis client with fallback to master in case of no slaves.
        No caching done with clients.
        Even though it can be an improvement, it could lead to stale invalid clients in failovers. Maybe in the future.
        """
        if master:
            return self.connection_factory.connect_master()
        else:
            return self.connection_factory.connect_slave(force_slave)

    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None, client=None, nx=False, xx=False):
        """
        Persist a value to the cache, and set an optional expiration time.
        Also supports optional nx parameter. If set to True - will use redis setnx instead of set.
        """
        nkey = self.make_key(key, version=version)
        nvalue = self.encode(value)

        if timeout == DEFAULT_TIMEOUT:
            timeout = self._backend.default_timeout

        # No need to limit this loop, because `redis.sentinel.MasterNotFoundError`
        # will be raised if `redis.sentinel.Sentinel` couldn't find a master
        # (in Redis Sentinel setup only master is used for writes).
        # But, it still possible, that Sentinels is accessible, but Redis itself
        # is not. In this case this loop become infinite.
        # If you wanna limit num tries, set `REDIS_SERVER_CONNECT_MAX_TRIES` in
        # `OPTIONS` section to value greater then 0.
        tries = self._options.get('REDIS_SERVER_CONNECT_MAX_TRIES', -1)
        while tries:
            try:
                if not client:
                    client = self.get_client(write=True)

                if timeout is not None:
                    # Convert to milliseconds
                    timeout = int(timeout * 1000)

                    if timeout <= 0:
                        if nx:
                            # Using negative timeouts when nx is True should
                            # not expire (in our case delete) the value if it exists.
                            # Obviously expire not existent value is noop.
                            return not self.has_key(key, version=version, client=client)
                        else:
                            # redis doesn't support negative timeouts in ex flags
                            # so it seems that it's better to just delete the key
                            # than to set it and than expire in a pipeline
                            return self.delete(key, client=client, version=version)

                return client.set(nkey, nvalue, nx=nx, px=timeout, xx=xx)
            except _main_exceptions as e:
                tries -= 1
                continue

    def close(self, **kwargs):
        """
        Nothing to close, because each method calls `get_client()`, which
        creates new connection.
        """
