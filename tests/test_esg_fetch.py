from moto import mock_aws
import boto3
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import esg.fetch_scores as fs


def test_fetch_scores(monkeypatch):
    data = [{"esg_score": 80}, {"carbon_score": 10, "diversity_score": 5}]
    it = iter(data)

    def fake_fetch(url):
        return next(it)

    monkeypatch.setattr(fs, "_fetch", fake_fetch)
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="esg-cache")
        df = fs.fetch_scores(["AAPL"])
        assert isinstance(df, pd.DataFrame)
        assert df.iloc[0]["esg_score"] == 80
        objs = s3.list_objects(Bucket="esg-cache")
        assert objs.get("Contents")
