"""Context manager for enforcing execution time limits."""
from __future__ import annotations

import signal
from contextlib import contextmanager
from typing import Iterator


class TimeboxTimeoutError(TimeoutError):
    """Raised when the timebox duration is exceeded."""


@contextmanager
def timebox(seconds: float) -> Iterator[None]:
    """Raise :class:`TimeboxTimeoutError` if enclosed block exceeds ``seconds``.

    Parameters
    ----------
    seconds:
        Maximum allowed execution time in seconds.
    """
    if seconds <= 0:
        raise ValueError("Seconds must be positive")

    def _handle(signum, frame):  # pragma: no cover - signal handler
        raise TimeboxTimeoutError(f"Operation exceeded {seconds} seconds")

    previous_handler = signal.signal(signal.SIGALRM, _handle)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)
