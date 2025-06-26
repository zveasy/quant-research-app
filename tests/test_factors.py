# In: tests/test_factors.py

import numpy as np
import pandas as pd

# Import all the factor functions you've created
from factors.value import get_price_to_book
from factors.quality import get_debt_to_equity, get_return_on_equity
from factors.momentum import get_12m_momentum
from factors.volatility import get_annualized_volatility

# --- Test Data ---
# A list of symbols to test against. One likely to work, one likely to fail.
VALID_SYMBOL = "AAPL"
INVALID_SYMBOL = "INVALID_SYMBOL_XYZ"


# --- Helper Function for Testing ---
def check_factor_output(value):
    """Checks if the output is either a valid float or a numpy NaN."""
    # The result should be a float or a numpy float64 for valid numbers,
    # or a float NaN for missing data.
    assert isinstance(value, (float, np.floating)) or pd.isna(value)


# --- PyTest Cases ---


def test_price_to_book():
    """Tests the Price-to-Book value factor."""
    check_factor_output(get_price_to_book(VALID_SYMBOL))
    # Test that an invalid symbol returns NaN
    assert pd.isna(get_price_to_book(INVALID_SYMBOL))


def test_debt_to_equity():
    """Tests the Debt-to-Equity quality factor."""
    check_factor_output(get_debt_to_equity(VALID_SYMBOL))
    assert pd.isna(get_debt_to_equity(INVALID_SYMBOL))


def test_return_on_equity():
    """Tests the Return on Equity quality factor."""
    check_factor_output(get_return_on_equity(VALID_SYMBOL))
    assert pd.isna(get_return_on_equity(INVALID_SYMBOL))


def test_12m_momentum():
    """Tests the 12-month Momentum factor."""
    check_factor_output(get_12m_momentum(VALID_SYMBOL))
    assert pd.isna(get_12m_momentum(INVALID_SYMBOL))


def test_annualized_volatility():
    """Tests the Annualized Volatility factor."""
    check_factor_output(get_annualized_volatility(VALID_SYMBOL))
    assert pd.isna(get_annualized_volatility(INVALID_SYMBOL))
