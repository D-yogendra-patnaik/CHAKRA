.PHONY: run test lint docker-build docker-up docker-down

run:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

lint:
	# Assume black/flake8 are installed
	@echo "Linting..."
	# black src/ tests/
	# isort src/ tests/
	# mypy src/

docker-build:
	docker build -t chakra-api:latest .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down
