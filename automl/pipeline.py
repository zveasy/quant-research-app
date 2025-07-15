"""AutoML pipeline using H2O and MLflow."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import boto3
import h2o
import mlflow
import pandas as pd
from h2o.automl import H2OAutoML


FEATURES_PATH = os.environ.get("FEATURES_PATH")
S3_OUTPUT_BUCKET = os.environ.get("OUTPUT_BUCKET")


def load_features(path: str) -> pd.DataFrame:
    if path.startswith("s3://"):
        bucket, key = path[5:].split("/", 1)
        tmp = Path(tempfile.mkstemp()[1])
        boto3.client("s3").download_file(bucket, key, str(tmp))
        df = pd.read_parquet(tmp)
        tmp.unlink()
        return df
    return pd.read_parquet(path)


def main() -> None:
    df = load_features(FEATURES_PATH)
    n = len(df)
    train, valid, test = df.iloc[: int(0.6 * n)], df.iloc[int(0.6 * n) : int(0.8 * n)], df.iloc[int(0.8 * n) :]

    h2o.init()
    train_h2o = h2o.H2OFrame(train)
    valid_h2o = h2o.H2OFrame(valid)

    target = train.columns[-1]
    aml = H2OAutoML(max_runtime_secs=3600, seed=1)
    aml.train(y=target, training_frame=train_h2o, validation_frame=valid_h2o)

    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "./mlruns"))
    with mlflow.start_run() as run:
        model_info = mlflow.h2o.log_model(aml.leader, artifact_path="model")
        sharpe = float(train[target].mean() / train[target].std())
        turnover = float(train[target].diff().abs().sum())
        mlflow.log_metric("sharpe", sharpe)
        mlflow.log_metric("turnover", turnover)
        best_model_path = model_info.model_uri

    if S3_OUTPUT_BUCKET:
        boto3.client("s3").put_object(
            Bucket=S3_OUTPUT_BUCKET,
            Key="automl_leader.txt",
            Body=best_model_path.encode(),
        )


if __name__ == "__main__":
    main()
