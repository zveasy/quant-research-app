# In: tests/test_option_pricing.py

import pytest
from option_pricing.black_scholes import black_scholes_price


def test_black_scholes_call_put():
    """Verify Black-Scholes prices for a known set of parameters."""
    call = black_scholes_price(100, 100, 1, 0.05, 0.2, "call")
    put = black_scholes_price(100, 100, 1, 0.05, 0.2, "put")
    assert call == pytest.approx(10.4506, rel=1e-3)
    assert put == pytest.approx(5.5735, rel=1e-3)


def test_invalid_option_type():
    """Ensure an invalid option type raises a ValueError."""
    with pytest.raises(ValueError):
        black_scholes_price(100, 100, 1, 0.05, 0.2, "invalid")

