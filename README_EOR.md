# Equity Options Research

Utilities for exploring equity options data using the [Polygon.io](https://polygon.io) API.

## Setup

1. Ensure Python 3.11 is installed.
2. Install dependencies and the package:

```bash
make setup
```

## API Key

Set your Polygon API key via the `POLYGON_API_KEY` environment variable:

```bash
export POLYGON_API_KEY=your_key_here
```

## Example

```bash
python -c "from src.polygon_client import PolygonClient; c=PolygonClient(); print(c.get_aggregates_df('AAPL',1,'day','2024-01-01','2024-01-05').head())"
```

## Development

- Lint the code:

```bash
make lint
```

- Run tests:

```bash
make test
```

