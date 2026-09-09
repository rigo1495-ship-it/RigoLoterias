from app.core.rate_limit import SlidingWindowRateLimiter


def test_sliding_window_rejects_then_recovers() -> None:
    limiter = SlidingWindowRateLimiter(maximum=2, window_seconds=10)
    assert limiter.allow("peer", now=100)
    assert limiter.allow("peer", now=101)
    assert not limiter.allow("peer", now=102)
    assert limiter.allow("peer", now=111)
