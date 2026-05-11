.PHONY: install test lint typecheck run-scenarios grade-local clean

install:
	pip install -e '.[dev]'

test:
	pytest

lint:
	ruff check src tests

typecheck:
	mypy src

run-scenarios:
	python -m langgraph_agent_lab.cli run-scenarios --config configs/lab.yaml --output outputs/metrics.json

run-scenarios-hidden:
	python -m langgraph_agent_lab.cli run-scenarios --config configs/lab_hidden.yaml --output outputs/metrics_hidden.json

grade-local:
	python -m langgraph_agent_lab.cli validate-metrics --metrics outputs/metrics.json

grade-local-hidden:
	python -m langgraph_agent_lab.cli validate-metrics --metrics outputs/metrics_hidden.json

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov dist build *.egg-info outputs/*.json
