"""Redis-backed cache dependency for FastAPI routes.

Inject once via ``Depends(get_cache)`` and call methods inline::

    async def handler(cache: Annotated[Cache, Depends(get_cache)], ...):
        cached = await cache.get('admin_users', suffix='page=1')
        if cached is not None:
            return cached

        result = await use_case.execute(...)
        await cache.create('admin_users', result, ttl=30, suffix='page=1')
        return result

        # Invalidate on mutation:
        await cache.invalidate('admin_users')              # entire resource
        await cache.invalidate('admin_users', suffix='1')  # specific entry
"""

import json
from collections.abc import Awaitable, Callable
from typing import Annotated, Any

import redis.asyncio as aioredis
from fastapi import Depends
from fastapi.encoders import jsonable_encoder

from app.config.redis import get_redis

_RedisDep = Annotated[aioredis.Redis, Depends(get_redis)]


class Cache:
    """Redis cache helper injected as a FastAPI dependency.

    All configuration (resource name, TTL, suffix) is provided at the call
    site, not at injection time. A single instance covers all resources
    needed within one request.

    Redis key format::

        applika:cache:{resource}
        applika:cache:{resource}:{suffix}
    """

    def __init__(self, redis: aioredis.Redis):
        self._redis = redis

    def _key(self, resource: str, suffix: str = '') -> str:
        base = f'applika:cache:{resource}'
        return f'{base}:{suffix}' if suffix else base

    async def get(
        self, resource: str, *, suffix: str = ''
    ) -> tuple[Any | None, Callable[..., Awaitable[None]]]:
        """Retrieve a cached value and a setter bound to the same key.

        :param resource: Cache namespace (e.g. ``'admin_users'``).
        :param suffix: Optional key suffix (e.g. ``'page=1:per_page=25'``).
        :returns: ``(value, setter)`` — ``value`` is the deserialized cached
            data or ``None`` on a miss; ``setter`` is an async callable
            ``setter(data, *, ttl)`` that stores a value under the same key.
        """
        raw = await self._redis.get(self._key(resource, suffix))
        value = json.loads(raw) if raw is not None else None

        async def setter(data: Any, *, ttl: int) -> None:
            await self.create(resource, data, ttl=ttl, suffix=suffix)

        return value, setter

    async def create(
        self, resource: str, data: Any, *, ttl: int, suffix: str = ''
    ) -> None:
        """Store a value in the cache.

        Serializes ``data`` via :func:`~fastapi.encoders.jsonable_encoder`,
        so Pydantic models and DTOs are handled automatically.

        :param resource: Cache namespace.
        :param data: Value to cache.
        :param ttl: Time-to-live in seconds.
        :param suffix: Optional key suffix.
        """
        await self._redis.setex(
            self._key(resource, suffix),
            ttl,
            json.dumps(jsonable_encoder(data)),
        )

    async def invalidate(self, resource: str, *, suffix: str = '') -> int:
        """Delete cache entries for a resource.

        Uses cursor-based ``SCAN`` to avoid blocking Redis.

        - ``invalidate('admin_users')`` — deletes the exact resource key
          and all suffixed variants.
        - ``invalidate('admin_users', suffix='page=1')`` — deletes only keys
          whose suffix starts with ``page=1``.

        :param resource: Cache namespace to target.
        :param suffix: Suffix fragment to narrow the deletion scope.
        :returns: Number of keys deleted.
        """
        if suffix:
            pattern = f'applika:cache:{resource}:{suffix}*'
            keys = [k async for k in self._redis.scan_iter(match=pattern)]
        else:
            base = f'applika:cache:{resource}'
            keys = [k async for k in self._redis.scan_iter(match=f'{base}:*')]
            if await self._redis.exists(base):
                keys.append(base)

        if not keys:
            return 0
        return await self._redis.delete(*keys)


async def get_cache(redis: _RedisDep) -> Cache:
    """FastAPI dependency factory for :class:`Cache`.

    :param redis: Injected async Redis client.
    :returns: A :class:`Cache` instance bound to the current request's Redis connection.
    """
    return Cache(redis)
