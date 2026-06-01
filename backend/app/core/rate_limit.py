"""Fixed-window rate limiting via Redis, usable as a FastAPI dependency.

Provides :class:`RateLimit`, a callable class designed to be passed to
``dependencies=[Depends(...)]`` on a route decorator. On each request it
increments a Redis counter for the current time window and raises
``HTTP 429`` when the limit is exceeded.
"""

import time
from typing import Annotated, Literal

import jwt
import redis.asyncio as aioredis
from fastapi import Depends, HTTPException, Request

from app.config.redis import get_redis
from app.config.settings import ACCESS_COOKIE_NAME, envs

_RedisDep = Annotated[aioredis.Redis, Depends(get_redis)]


class RateLimit:
    """Fixed-window rate limiter backed by Redis.

    Instantiate once per route and pass to FastAPI's ``dependencies``
    parameter::

        @router.get('/path', dependencies=[Depends(RateLimit(60, 60, scope='user'))])
        async def handler(...): ...

    The Redis key encodes the scope identifier, the route path, and the
    current time window bucket so that keys expire naturally after ``window``
    seconds without a background job.

    Redis key format::

        applika:rate_limit:{scope}:{identifier}:{path}:{window_bucket}

    :param requests: Maximum number of requests allowed within ``window`` seconds.
    :param window: Length of the time window in seconds.
    :param scope: Determines the identifier used per key:

        - ``'user'`` — extracts ``sub`` from the ``__access`` JWT cookie
          (no database hit); falls back to client IP on decode failure.
        - ``'ip'`` — uses the client IP address; suitable for public/unauthenticated routes.
        - ``'global'`` — one shared counter for all callers of the route.
    """

    def __init__(
        self,
        requests: int,
        window: int,
        scope: Literal['global', 'user', 'ip'] = 'user',
    ):
        self.requests = requests
        self.window = window
        self.scope = scope

    async def __call__(self, request: Request, redis: _RedisDep) -> None:
        """Check and increment the rate limit counter for this request.

        :param request: The current HTTP request.
        :param redis: Injected async Redis client.
        :raises HTTPException: ``429 Too Many Requests`` with a ``Retry-After``
            header when the limit is exceeded.
        """
        key = self._build_key(request)
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, self.window)
        if count > self.requests:
            raise HTTPException(
                status_code=429,
                detail=f'Rate limit exceeded. Max {self.requests} requests per {self.window}s.',
                headers={'Retry-After': str(self.window)},
            )

    def _build_key(self, request: Request) -> str:
        """Construct the Redis key for the current request and time window.

        :param request: The current HTTP request.
        :returns: A colon-delimited Redis key string.
        """
        bucket = int(time.time()) // self.window
        identifier = self._identifier(request)
        return f'applika:rate_limit:{self.scope}:{identifier}:{request.url.path}:{bucket}'

    def _identifier(self, request: Request) -> str:
        """Resolve the scope-specific identifier for the rate limit key.

        :param request: The current HTTP request.
        :returns: A string identifier: user ID, client IP, or ``'global'``.
        """
        if self.scope == 'ip':
            return request.client.host or 'unknown'
        if self.scope == 'user':
            token = request.cookies.get(ACCESS_COOKIE_NAME, '')
            try:
                payload = jwt.decode(
                    token,
                    envs.JWT_SECRET,
                    algorithms=[envs.JWT_ALGORITHM],
                )
                return str(payload.get('sub', 'anonymous'))
            except Exception:
                return request.client.host or 'unknown'
        return 'global'
