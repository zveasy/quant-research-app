from engine.models.cost_model import CostModel, load_fixture_logs, mape


def test_cost_model_accuracy():
    df = load_fixture_logs()
    model = CostModel()
    est = model.estimate_is(df['latency_ms'].values, df['spread_bps'].values)
    error = mape(df['is_bps'].values, est)
    assert error < 20.0, f"MAPE {error:.2f}% exceeds 20% threshold"
