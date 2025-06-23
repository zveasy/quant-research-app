# In: tests/test_alt_data.py

import pytest
import pandas as pd

# Import the function we want to test
from alt_data.trends import get_google_trends_score

# --- Test Data ---
VALID_KEYWORD = "AAPL"
# A nonsense keyword that is very unlikely to have any search trends
INVALID_KEYWORD = "ASDFQWERZXCV" 

# --- PyTest Cases ---

def test_google_trends_valid_keyword():
    """
    Tests that the Google Trends function returns a valid float for a real keyword.
    """
    # 1. Arrange & 2. Act
    score = get_google_trends_score(VALID_KEYWORD)

    # 3. Assert
    # The score should be a valid number (float). It can be positive, negative, or zero.
    assert isinstance(score, float)
    assert pd.notna(score)


def test_google_trends_invalid_keyword():
    """
    Tests that the Google Trends function returns 0.0 for a keyword
    that has no data, as defined in our error handling.
    """
    # 1. Arrange & 2. Act
    score = get_google_trends_score(INVALID_KEYWORD)

    # 3. Assert
    # For a keyword with no trend data, our function is designed to return 0.0
    assert score == 0.0

