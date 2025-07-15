import time
import yfinance as yf


def yf_download_retry(ticker: str, *args, retries: int = 3, delay: float = 1.0, **kwargs):
    """Download data with basic retry logic."""
    last_err = None
    for _ in range(retries):
        try:
            return yf.download(ticker, *args, progress=False, **kwargs)
        except Exception as e:
            last_err = e
            time.sleep(delay)
    raise last_err
