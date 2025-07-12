from political.legislation import fetch_recent_legislation, summarize_legislation


def test_fetch_recent_legislation_dev_mode():
    bills = fetch_recent_legislation(dev_mode=True)
    assert isinstance(bills, list)
    assert bills
    assert "title" in bills[0]


def test_summarize_legislation_dev_mode():
    text = "This act provides incentives for green energy projects."
    summary = summarize_legislation(text, dev_mode=True)
    assert "summary" in summary
    assert "impact" in summary
