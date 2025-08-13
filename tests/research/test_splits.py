import pandas as pd
import numpy as np
from research.splits import train_test_split, walk_forward_splits


def _make_index(n=100):
    return pd.date_range("2020-01-01", periods=n, freq="D")


def test_train_test_split_fraction():
    idx = _make_index(50)
    train, test = train_test_split(idx, test_size=0.2)
    assert train.sum() == 40
    assert test.sum() == 10
    assert np.all(~(train & test))
    assert np.all(train | test)


def test_train_test_split_int():
    idx = _make_index(30)
    train, test = train_test_split(idx, test_size=5)
    assert test.sum() == 5
    assert train.sum() == 25


def test_walk_forward_non_overlapping():
    idx = _make_index(30)
    splits = walk_forward_splits(idx, train_size=10, test_size=5)
    # Expect (30-10)/5 = 4 windows but last may drop remainder -> 4
    assert len(splits) == 4
    for train, test in splits:
        assert train.sum() == 10
        assert test.sum() == 5
        # no overlap between train and test
        assert np.all(~(train & test))


def test_walk_forward_step_smaller():
    idx = _make_index(40)
    splits = walk_forward_splits(idx, train_size=10, test_size=5, step=2)
    # Ensure at least first split masks length matches index length
    train, test = splits[0]
    assert len(train) == len(idx) == 40
