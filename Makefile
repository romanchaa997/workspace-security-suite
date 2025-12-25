.PHONY: help install dev test lint format clean build deploy logs

help:
	@echo "Workspace Security Suite - Available Commands"
	@echo "make install - Install dependencies"
	@echo "make dev - Start development environment"
	@echo "make test - Run test suite"
	@echo "make lint - Run code linting"

install:
	pip install -r requirements.txt

dev:
	docker-compose up -d

test:
	pytest --cov=. --cov-report=html

test-unit:
	pytest tests/ -m unit

lint:
	flake8 . --exclude=venv,build

format:
	black . --exclude=venv

clean:
	rm -rf build/ dist/ htmlcov/

build:
	docker build -t workspace-security-suite:latest .

deploy:
	docker-compose -f docker-compose.yml up -d

logs:
	docker-compose logs -f
