"""Login throttling (in-process sliding window).

Per IP + email it slows down password guessing on one account; per IP it caps
credential stuffing across accounts. State is per API process; behind several
processes put the same limit on the reverse proxy as well.
"""

from __future__ import annotations

import threading
import time
from collections import deque


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


class LoginThrottle:
    def __init__(self, per_account: int, window_minutes: int) -> None:
        window = window_minutes * 60
        self.account = SlidingWindow(per_account, window)
        self.address = SlidingWindow(per_account * 5, window)

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
