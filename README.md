# FastAPI Backend Template

Стартовый шаблон для backend-приложений на FastAPI с архитектурой, ориентированной на предметную область (DDD).

## Возможности

-   FastAPI с поддержкой async/await
-   Архитектура DDD: разделение на домены, инфраструктуру, презентацию и прикладной слой
-   Docker-контейнеризация (PostgreSQL)
-   Автоматическая документация Swagger и ReDoc
-   JWT-аутентификация
-   SQLAlchemy 2.0 + Alembic для работы с БД
-   Миграции с автоматическими повторными попытками подключения
-   Статический анализ типов (mypy) и линтинг (ruff)
-   Pre-commit хуки
-   Управление зависимостями через Poetry

## Структура проекта

```text
fastapi_backend_template/
├── .env.example              # Пример переменных окружения
├── .pre-commit-config.yaml   # Конфигурация pre-commit хуков
├── Makefile                  # Команды автоматизации
├── README.md                 # Документация проекта
├── alembic.ini               # Конфигурация Alembic
├── docker-compose.yml        # Конфигурация Docker Compose
├── mypy.ini                  # Конфигурация mypy
├── poetry.lock               # Блокировка зависимостей
├── pyproject.toml            # Метаданные и зависимости проекта
├── migrations/               # Миграции базы данных (Alembic)
│   ├── env.py
│   ├── script.py.mako
│   └── versions/             # Файлы миграций
└── src/                      # Исходный код приложения
    ├── main.py               # Точка входа FastAPI
    ├── routers.py            # Регистрация маршрутов
    ├── application/          # Прикладной слой (use cases, DTO)
    │   └── users/
    ├── common/               # Общие модули (конфиги, исключения, логирование)
    ├── di/                   # Dependency Injection
    ├── domains/              # Доменный слой (сущности, value objects, сервисы)
    │   ├── auth/
    │   └── users/
    ├── infrastructure/       # Инфраструктурный слой (БД, внешние сервисы)
    │   ├── auth/
    │   └── database/
    └── presentation/         # Слой презентации (роутеры, схемы запросов/ответов)
        └── user/