# In: tests/test_option_pricing.py

import pytest
from option_pricing.black_scholes import black_scholes_price
from option_pricing.analytics import (
    black_scholes_delta,
    black_scholes_gamma,
    black_scholes_vega,
    black_scholes_theta,
    black_scholes_rho,
    implied_volatility,
)


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




def test_black_scholes_greeks():
    """Check a few Black-Scholes Greeks against reference values."""
    delta = black_scholes_delta(100, 100, 1, 0.05, 0.2, "call")
    gamma = black_scholes_gamma(100, 100, 1, 0.05, 0.2)
    vega = black_scholes_vega(100, 100, 1, 0.05, 0.2)
    theta = black_scholes_theta(100, 100, 1, 0.05, 0.2, "call")
    rho = black_scholes_rho(100, 100, 1, 0.05, 0.2, "call")

    assert delta == pytest.approx(0.6368, rel=1e-3)
    assert gamma == pytest.approx(0.01876, rel=1e-3)
    assert vega == pytest.approx(37.524, rel=1e-3)
    assert theta == pytest.approx(-6.4140, rel=1e-3)
    assert rho == pytest.approx(53.232, rel=1e-3)


def test_implied_volatility():
    """Ensure implied volatility recovers the input volatility."""
    call_price = black_scholes_price(100, 100, 1, 0.05, 0.2, "call")
    vol = implied_volatility(call_price, 100, 100, 1, 0.05, "call")
    assert vol == pytest.approx(0.2, rel=1e-4)


