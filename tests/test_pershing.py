import pathlib

import vcr

from integrations.pershing import PershingAdapter

cassette = pathlib.Path(__file__).with_suffix('.yaml')


@vcr.use_cassette(str(cassette))
def test_pershing_mapping(requests_mock):
    base_url = 'https://example.com'
    adapter = PershingAdapter(base_url, 'token')
    requests_mock.get(f'{base_url}/positions', json=[{
        'accountId': '1', 'symbol': 'AAPL', 'quantity': '10', 'price': '150', 'tradeDate': '2024-01-01T00:00:00Z'
    }])
    requests_mock.get(f'{base_url}/trades', json=[{
        'accountId': '1', 'symbol': 'AAPL', 'quantity': '5', 'price': '149', 'tradeDate': '2024-01-02T00:00:00Z'
    }])
    positions = adapter.positions()
    trades = adapter.trades()
    assert positions[0]['symbol'] == 'AAPL'
    assert trades[0]['qty'] == 5.0
