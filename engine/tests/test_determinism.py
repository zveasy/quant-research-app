from pathlib import Path
from engine.backtest import run_backtest, parquet_sha256, write_parquet


def test_deterministic_sha256(tmp_path):
    """Two runs must produce identical sha256 and match golden file."""
    df1 = run_backtest()
    df2 = run_backtest()
    assert df1.equals(df2)

    h1 = parquet_sha256(df1)
    h2 = parquet_sha256(df2)
    assert h1 == h2

    # Golden file path
    golden_path = Path(__file__).resolve().parent.parent / "fixtures/golden/run.parquet"
    golden_path.parent.mkdir(parents=True, exist_ok=True)

    if golden_path.exists():
        import pandas as pd
        g_df = pd.read_parquet(golden_path)
        assert parquet_sha256(g_df) == h1, "Backtest output drifted from golden fixture"
    else:
        # First run will write the golden file so that subsequent CI runs compare against it.
        write_parquet(df1, golden_path)
