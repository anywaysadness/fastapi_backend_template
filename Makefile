# Переменные
PYTHON = python
PIP = pip
VENV = .venv
APP_DIR = src
HOST = 0.0.0.0
PORT = 8000
DOCKER_COMPOSE = docker-compose

## Запуск FastAPI приложения
start: venv
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

.PHONY: start venv clean