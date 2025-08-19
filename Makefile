.PHONY: setup lint test

setup:
	python -m pip install --upgrade pip
	python -m pip install -e .[dev]

lint:
	ruff src tests/test_eor_*.py

test:
	PYTHONPATH=src pytest tests/test_eor_*.py -vv
