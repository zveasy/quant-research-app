"""Black-Scholes Greeks and implied volatility calculator."""

from __future__ import annotations

from math import exp, log, sqrt

from scipy.stats import norm

from .black_scholes import black_scholes_price, OptionType


# Internal helper functions ----------------------------------------------------

def _d1(
    spot_price: float,
    strike: float,
    time_to_maturity: float,
    risk_free_rate: float,
    volatility: float,
) -> float:
    return (
        log(spot_price / strike)
        + (risk_free_rate + 0.5 * volatility**2) * time_to_maturity
    ) / (volatility * sqrt(time_to_maturity))


def _d2(d1: float, volatility: float, time_to_maturity: float) -> float:
    return d1 - volatility * sqrt(time_to_maturity)


# Public API -------------------------------------------------------------------

def black_scholes_delta(
    spot_price: float,
    strike: float,
    time_to_maturity: float,
    risk_free_rate: float,
    volatility: float,
    option_type: OptionType = "call",
) -> float:
    """Calculate the Black-Scholes delta for a European option."""
    if time_to_maturity <= 0:
        raise ValueError("time_to_maturity must be positive")
    if volatility <= 0:
        raise ValueError("volatility must be positive")
    d1 = _d1(spot_price, strike, time_to_maturity, risk_free_rate, volatility)
    if option_type == "call":
        return norm.cdf(d1)
    elif option_type == "put":
        return -norm.cdf(-d1)
    raise ValueError("option_type must be 'call' or 'put'")


def black_scholes_gamma(
    spot_price: float,
    strike: float,
    time_to_maturity: float,
    risk_free_rate: float,
    volatility: float,
) -> float:
    """Calculate the Black-Scholes gamma for a European option."""
    if time_to_maturity <= 0:
        raise ValueError("time_to_maturity must be positive")
    if volatility <= 0:
        raise ValueError("volatility must be positive")
    d1 = _d1(spot_price, strike, time_to_maturity, risk_free_rate, volatility)
    return norm.pdf(d1) / (spot_price * volatility * sqrt(time_to_maturity))


def black_scholes_vega(
    spot_price: float,
    strike: float,
    time_to_maturity: float,
    risk_free_rate: float,
    volatility: float,
) -> float:
    """Calculate the Black-Scholes vega for a European option."""
    if time_to_maturity <= 0:
        raise ValueError("time_to_maturity must be positive")
    if volatility <= 0:
        raise ValueError("volatility must be positive")
    d1 = _d1(spot_price, strike, time_to_maturity, risk_free_rate, volatility)
    return spot_price * norm.pdf(d1) * sqrt(time_to_maturity)


def black_scholes_theta(
    spot_price: float,
    strike: float,
    time_to_maturity: float,
    risk_free_rate: float,
    volatility: float,
    option_type: OptionType = "call",
) -> float:
    """Calculate the Black-Scholes theta for a European option."""
    if time_to_maturity <= 0:
        raise ValueError("time_to_maturity must be positive")
    if volatility <= 0:
        raise ValueError("volatility must be positive")
    d1 = _d1(spot_price, strike, time_to_maturity, risk_free_rate, volatility)
    d2 = _d2(d1, volatility, time_to_maturity)
    common = -(spot_price * norm.pdf(d1) * volatility) / (2 * sqrt(time_to_maturity))
    if option_type == "call":
        return common - risk_free_rate * strike * exp(-risk_free_rate * time_to_maturity) * norm.cdf(d2)
    elif option_type == "put":
        return common + risk_free_rate * strike * exp(-risk_free_rate * time_to_maturity) * norm.cdf(-d2)
    raise ValueError("option_type must be 'call' or 'put'")


def black_scholes_rho(
    spot_price: float,
    strike: float,
    time_to_maturity: float,
    risk_free_rate: float,
    volatility: float,
    option_type: OptionType = "call",
) -> float:
    """Calculate the Black-Scholes rho for a European option."""
    if time_to_maturity <= 0:
        raise ValueError("time_to_maturity must be positive")
    if volatility <= 0:
        raise ValueError("volatility must be positive")
    d1 = _d1(spot_price, strike, time_to_maturity, risk_free_rate, volatility)
    d2 = _d2(d1, volatility, time_to_maturity)
    if option_type == "call":
        return strike * time_to_maturity * exp(-risk_free_rate * time_to_maturity) * norm.cdf(d2)
    elif option_type == "put":
        return -strike * time_to_maturity * exp(-risk_free_rate * time_to_maturity) * norm.cdf(-d2)
    raise ValueError("option_type must be 'call' or 'put'")


def implied_volatility(
    price: float,
    spot_price: float,
    strike: float,
    time_to_maturity: float,
    risk_free_rate: float,
    option_type: OptionType = "call",
    initial_guess: float = 0.2,
    tolerance: float = 1e-6,
    max_iterations: int = 100,
) -> float:
    """Solve for the implied volatility using the Newton-Raphson method."""
    if time_to_maturity <= 0:
        raise ValueError("time_to_maturity must be positive")
    vol = initial_guess
    for _ in range(max_iterations):
        bs_price = black_scholes_price(
            spot_price,
            strike,
            time_to_maturity,
            risk_free_rate,
            vol,
            option_type,
        )
        vega = black_scholes_vega(
            spot_price,
            strike,
            time_to_maturity,
            risk_free_rate,
            vol,
        )
        price_diff = bs_price - price
        if abs(price_diff) < tolerance:
            return vol
        vol -= price_diff / vega
    raise RuntimeError("implied volatility failed to converge")

