.PHONY: setup test lint format demo-all clean docker-build docker-test

setup:
	python -m venv venv
	./venv/Scripts/pip install -r requirements.txt

test:
	pytest -v --cov=app tests/

lint:
	ruff check .
	mypy app scripts tests

format:
	black .
	ruff check --fix .

demo-all:
	python scripts/part1_tree.py
	python scripts/part2_fetch.py
	python scripts/part3_verify.py

clean:
	rm -rf __pycache__ .pytest_cache .coverage .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

docker-build:
	docker-compose build

docker-test:
	docker-compose up app

docker-demo:
	docker-compose up demo
