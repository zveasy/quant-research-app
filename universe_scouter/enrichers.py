import pandas as pd
import numpy as np
import yfinance as yf
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
import warnings
import traceback

# Suppress routine statsmodels warnings
warnings.filterwarnings("ignore", category=UserWarning, module="statsmodels")


def get_predictability_score(symbol: str, period: str = "1y") -> float:
    """
    Calculates a predictability score using a more stable ARIMA model
    and includes detailed value inspection.
    """
    try:
        # 1. Fetch historical data
        stock_data = yf.download(
            symbol, period=period, progress=False, auto_adjust=True
        )
        if stock_data.empty or len(stock_data) < 100:
            print(
                f"   - FAIL: Downloaded only {len(stock_data)} rows. Need at least 100."
            )
            return np.nan

        # 2. Ensure daily frequency and forward-fill missing values
        prices = stock_data["Close"].asfreq("D").ffill()

        # 3. Split data into training and testing sets
        train_size = int(len(prices) * 0.8)
        train, test = prices[0:train_size], prices[train_size:]

        # 4. Fit a more stable ARIMA model with order=(1, 1, 1)
        model = ARIMA(train, order=(1, 1, 1))
        model_fit = model.fit()

        # 5. Make predictions
        predictions = model_fit.forecast(steps=len(test))

        # 6. Calculate and normalize RMSE
        rmse = np.sqrt(mean_squared_error(test, predictions))
        normalized_rmse = rmse / test.mean()

        # --- FINAL VALUE INSPECTION ---
        print("\n   --- Final Value Check ---")
        print(f"   - Raw RMSE value: {rmse}")
        print(f"   - Final Normalized RMSE value: {normalized_rmse}")
        print("   -------------------------\n")

        # Final check to prevent returning an invalid number
        if not np.isfinite(normalized_rmse).all():
            print(
                "   - FAIL: Final score is NaN or infinity. Model is unstable for this data."
            )
            return np.nan
        # Extract the single float value from the Series
        return normalized_rmse.item()

    except Exception:
        print(f"\n❌ An unexpected error occurred for symbol '{symbol}':")
        traceback.print_exc()
        return np.nan


# --- To test this function directly ---
if __name__ == "__main__":
    aapl_symbol = "AAPL"
    print(f"Calculating predictability for {aapl_symbol}...")

    predict_score = get_predictability_score(aapl_symbol)

    if isinstance(predict_score, float) and pd.notna(predict_score):
        print(
            f"\n📈 Predictability Score (Normalized RMSE) for {aapl_symbol}: {predict_score:.4f}"
        )
        print("(Lower is better)")
    else:
        print(f"\nCould not calculate predictability for {aapl_symbol}.")
