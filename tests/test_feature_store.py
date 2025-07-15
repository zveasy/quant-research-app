import pandas as pd
import pandas as pd
from feature_store import save, load, FEATURE_STORE_ROOT


def test_round_trip(tmp_path, monkeypatch):
    monkeypatch.setenv("FEATURE_STORE_ROOT", str(tmp_path))
    df = pd.DataFrame({"a": [1, 2]})
    save(df, "tbl", "2024-01-01")
    out = load("tbl").collect().to_pandas()
    pd.testing.assert_frame_equal(out, df)


def test_date_filter(tmp_path, monkeypatch):
    monkeypatch.setenv("FEATURE_STORE_ROOT", str(tmp_path))
    df1 = pd.DataFrame({"a": [1]})
    df2 = pd.DataFrame({"a": [2]})
    save(df1, "tbl", "2024-01-01")
    save(df2, "tbl", "2024-01-02")
    out = load("tbl", date_from="2024-01-02").collect().to_pandas()
    pd.testing.assert_frame_equal(out, df2)
