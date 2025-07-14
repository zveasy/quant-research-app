"""Simple Black-Scholes option pricing model."""

from math import exp, log, sqrt
from typing import Literal

from scipy.stats import norm


OptionType = Literal["call", "put"]


def black_scholes_price(
    spot_price: float,
    strike: float,
    time_to_maturity: float,
    risk_free_rate: float,
    volatility: float,
    option_type: OptionType = "call",
) -> float:
    """Calculates the Black-Scholes price for a European option.

    Args:
        spot_price: Current underlying price.
        strike: Option strike price.
        time_to_maturity: Time to maturity in years.
        risk_free_rate: Risk-free interest rate as a decimal.
        volatility: Annualized volatility of returns as a decimal.
        option_type: Either ``"call"`` or ``"put"``.

    Returns:
        float: Option price.
    """
    if time_to_maturity <= 0:
        raise ValueError("time_to_maturity must be positive")
    if volatility <= 0:
        raise ValueError("volatility must be positive")

    d1 = (
        log(spot_price / strike)
        + (risk_free_rate + 0.5 * volatility ** 2) * time_to_maturity
    ) / (volatility * sqrt(time_to_maturity))
    d2 = d1 - volatility * sqrt(time_to_maturity)

    if option_type == "call":
        return spot_price * norm.cdf(d1) - strike * exp(-risk_free_rate * time_to_maturity) * norm.cdf(d2)
    elif option_type == "put":
        return strike * exp(-risk_free_rate * time_to_maturity) * norm.cdf(-d2) - spot_price * norm.cdf(-d1)
    else:
        raise ValueError("option_type must be 'call' or 'put'")

