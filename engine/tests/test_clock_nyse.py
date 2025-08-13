from pathlib import Path
import pandas as pd

CSV = Path(__file__).resolve().parent.parent / "fixtures/clock/nyse.csv"

HOLIDAYS = {
    "2024-01-01",
    "2024-01-15",
    "2024-02-19",
    "2024-03-29",
    "2024-05-27",
    "2024-06-19",
    "2024-07-04",
    "2024-09-02",
    "2024-11-28",
    "2024-12-25",
}

EARLY_CLOSES = {
    "2024-07-03",
    "2024-11-29",
    "2024-12-24",
}


def _load():
    return pd.read_csv(CSV, dtype={"date": str, "open_utc": str, "close_utc": str, "early_close": bool})


def test_holidays_excluded():
    df = _load()
    missing = HOLIDAYS & set(df["date"].values)
    assert not missing, f"Holiday dates present: {missing}"


def test_early_close_flags():
    df = _load()
    flagged = set(df.loc[df["early_close"], "date"].values)
    assert flagged == EARLY_CLOSES, "Early close flags mismatch"
    # Ensure close time 18:00 UTC for EDT or 18/19? Let's assert local 13:00 => 17:00/18:00
    for _, row in df[df["early_close"]].iterrows():
        assert row["close_utc"] in {"17:00", "18:00"}


def test_dst_offsets():
    df = _load().set_index("date")
    # A winter date (EST)
    assert df.loc["2024-01-02", "open_utc"] == "14:30"
    # A summer date (EDT)
    assert df.loc["2024-06-03", "open_utc"] == "13:30"
