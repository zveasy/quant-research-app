"""Tests for configuration utilities."""
import pytest

from src.config import get_settings


def test_missing_api_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("POLYGON_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        get_settings()


def test_reads_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POLYGON_API_KEY", "test-key")
    settings = get_settings()
    assert settings.polygon_api_key == "test-key"
