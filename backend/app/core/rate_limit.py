from collections import defaultdict, deque
from threading import Lock
from time import monotonic


class SlidingWindowRateLimiter:
    """Small process-local guard; a gateway is required for distributed deployments."""

    def __init__(self, maximum: int, window_seconds: int) -> None:
        if maximum < 1 or window_seconds < 1:
            raise ValueError("Rate-limit maximum and window must be positive")
        self.maximum = maximum
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str, now: float | None = None) -> bool:
        current = monotonic() if now is None else now
        cutoff = current - self.window_seconds
        with self._lock:
            requests = self._requests[key]
            while requests and requests[0] <= cutoff:
                requests.popleft()
            if len(requests) >= self.maximum:
                return False
            requests.append(current)
            return True
