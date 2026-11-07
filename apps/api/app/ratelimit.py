"""Rate limiting.

Login/sign-up/upload limits use a sliding window. The default backend is
in-process memory; ``RATE_LIMIT_BACKEND=redis`` shares counters across API
workers. If Redis is unreachable the limiter degrades to memory instead of
failing sign-in.
"""

from __future__ import annotations

import logging
import threading
import time
from collections import deque

from .config import settings

log = logging.getLogger("topiome.ratelimit")


class SlidingWindow:
    def __init__(self, limit: int, window_seconds: float) -> None:
        self.limit = limit
        self.window = window_seconds
        self._events: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def _prune(self, key: str, now: float) -> deque[float]:
        events = self._events.setdefault(key, deque())
        while events and now - events[0] > self.window:
            events.popleft()
        return events

    def retry_after(self, key: str) -> int | None:
        """Seconds until the next attempt is allowed, or None if allowed now."""
        now = time.monotonic()
        with self._lock:
            events = self._prune(key, now)
            if len(events) < self.limit:
                return None
            return max(1, int(self.window - (now - events[0])) + 1)

    def hit(self, key: str) -> None:
        now = time.monotonic()
        with self._lock:
            self._prune(key, now).append(now)

    def reset(self, key: str) -> None:
        with self._lock:
            self._events.pop(key, None)


class RedisWindow:
    """Fixed-window counters in Redis with an automatic memory fallback."""

    def __init__(self, limit: int, window_seconds: float, url: str) -> None:
        self.limit = limit
        self.window = int(window_seconds)
        self.url = url
        self.memory = SlidingWindow(limit, window_seconds)
        self.client = None
        self._connect()

    def _connect(self) -> None:
        try:
            import redis

            self.client = redis.from_url(self.url, decode_responses=True)
            self.client.ping()
        except Exception as exc:  # noqa: BLE001 - fallback is intentional
            log.warning("Redis rate limiter unavailable (%s); using memory", exc)
            self.client = None

    def _redis_key(self, key: str) -> str:
        return f"topiome:rl:{self.window}:{key}"

    def retry_after(self, key: str) -> int | None:
        if self.client is None:
            return self.memory.retry_after(key)
        try:
            redis_key = self._redis_key(key)
            value = int(self.client.get(redis_key) or 0)
            if value < self.limit:
                return None
            ttl = int(self.client.ttl(redis_key) or 0)
            return max(ttl, 1)
        except Exception:  # noqa: BLE001
            self.client = None
            return self.memory.retry_after(key)

    def hit(self, key: str) -> None:
        if self.client is None:
            self.memory.hit(key)
            return
        try:
            redis_key = self._redis_key(key)
            with self.client.pipeline() as pipe:
                pipe.incr(redis_key)
                pipe.expire(redis_key, self.window)
                pipe.execute()
        except Exception:  # noqa: BLE001
            self.client = None
            self.memory.hit(key)

    def reset(self, key: str) -> None:
        if self.client is None:
            self.memory.reset(key)
            return
        try:
            self.client.delete(self._redis_key(key))
        except Exception:  # noqa: BLE001
            self.client = None
            self.memory.reset(key)


def make_window(limit: int, window_seconds: float):
    if settings.rate_limit_backend == "redis":
        return RedisWindow(limit, window_seconds, settings.redis_url)
    return SlidingWindow(limit, window_seconds)


class LoginThrottle:
    def __init__(self, per_account: int, window_minutes: int) -> None:
        window = window_minutes * 60
        self.account = make_window(per_account, window)
        self.address = make_window(per_account * 5, window)

    def retry_after(self, ip: str, email: str) -> int | None:
        waits = [
            w
            for w in (self.account.retry_after(f"{ip}|{email}"), self.address.retry_after(ip))
            if w is not None
        ]
        return max(waits) if waits else None

    def failed(self, ip: str, email: str) -> None:
        self.account.hit(f"{ip}|{email}")
        self.address.hit(ip)

    def succeeded(self, ip: str, email: str) -> None:
        self.account.reset(f"{ip}|{email}")


register_limiter = make_window(settings.register_attempts_per_hour, 3600)
upload_limiter = make_window(settings.upload_attempts_per_hour, 3600)
