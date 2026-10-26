# Переменные
PYTHON = python
PIP = pip
VENV = .venv
APP_DIR = src
HOST = 0.0.0.0
PORT = 8000
DOCKER_COMPOSE = docker compose

## Установка зависимостей
install:
	poetry install

## Запуск FastAPI приложения
start:
	@echo "Запуск FastAPI приложения..."
	$(VENV)/bin/uvicorn $(APP_DIR).main:app --host $(HOST) --port $(PORT) --reload

## Поднятие контейнеров Docker
up:
	@echo "Поднятие контейнеров Docker..."
	$(DOCKER_COMPOSE) up -d

## Остановка контейнеров Docker
down:
	@echo "Остановка контейнеров Docker..."
	$(DOCKER_COMPOSE) down

## Создание новой миграции
migrate:
	@echo "Создание миграции alembic..."
	poetry run alembic revision --autogenerate -m "${NAME}"

## Применение миграций
upgrade:
	@echo "Применение миграций alembic..."
	poetry run alembic upgrade head

## Линтинг
lint:
	poetry run ruff check src tests migrations

## Проверка типов
typecheck:
	poetry run mypy src tests

## Тесты
test:
	poetry run pytest

.PHONY: install start up down migrate upgrade lint typecheck test
