"""Tests for the timebox utility."""

import time
import pytest

from src.utils.timebox import TimeboxTimeoutError, timebox


def test_timebox_completes() -> None:
    with timebox(1):
        time.sleep(0.1)


def test_timebox_times_out() -> None:
    with pytest.raises(TimeboxTimeoutError):
        with timebox(0.1):
            time.sleep(1)
