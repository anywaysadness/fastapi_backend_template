# FastAPI Backend Template

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI%2B-green)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](https://opensource.org/licenses/MIT)

Стартовый шаблон для быстрого развертывания backend-приложений на FastAPI.


## Содержание

- [Назначение](#назначение)
- [Особенности](#особенности)
- [Структура проекта](#структура-проекта)
- [Быстрый старт](#быстрый-старт)
- [Работа с миграциями](#работа-с-миграциями)


---
## Назначение

Этот шаблон создан для ускорения начала разработки новых проектов на FastAPI, предоставляя:
- Предварительно настроенную структуру проекта
- Готовые конфигурации для Docker и CI/CD
- Примеры реализации основных компонентов
- Интеграцию с популярными инструментами
---

## Особенности

- ⚡ FastAPI с async/await поддержкой
- 🐳 Docker-контейнеризация (образы для prod и dev)
- 📝 Автоматическая документация Swagger и ReDoc
- 🔒 Поддержка аутентификации (JWT)
- 🧪 Тестовая конфигурация с pytest
- 📊 Логирование настроено через Loguru
- 🛠️ Интеграция с SQLAlchemy (PostgreSQL/MySQL/SQLite)
- 🌐 CORS middleware предварительно настроен
- 🔄 Примеры CRUD эндпоинтов

---
## Структура проекта

```
fastapi_backend_template/
├── app/ # Основное приложение
│ ├── api/ # API эндпоинты
│ ├── core/ # Ядро приложения (config, security и т.д.)
│ ├── models/ # Pydantic и SQLAlchemy модели
│ ├── services/ # Бизнес-логика
│ └── main.py # Точка входа
├── tests/ # Тесты
├── migrations/ # Миграции базы данных (Alembic)
├── .env.example # Пример переменных окружения
├── requirements/ # Зависимости (dev/prod)
├── docker-compose.yml # Конфигурация Docker Compose
├── Dockerfile # Docker конфигурация
└── README.md # Документация
```
---
## Быстрый старт

1. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/anywaysadness/fastapi_backend_template.git
   cd fastapi_backend_template
   ```
2. **Создайте файл `.env`**:
   Скопируйте `.env.example` в `.env` и настройте переменные окружения:
   ```bash
   cp .env.example .env
   ```
3. **Установите зависимости**:
   ```bash
   poetry config virtualenvs.in-project true
   poetry install
   ```
4. **Запустите базу данных**:
   Для запуска базы данных PostgreSQL используйте Docker через Makefile:
    ```bash
   make up
   ```
   Эта команда поднимет контейнеры, описанные в docker-compose.yml.

   Приложение будет доступно на:
    API: http://localhost:8000

    Документация: http://localhost:8000/docs

    ReDoc: http://localhost:8000/redoc

## Работа с миграциями

Проект использует Alembic для управления миграциями. Вы можете управлять миграциями через `Makefile`.

1. **Создание новой миграции**:
   ```bash
   make migrate NAME="migration_name"
   ```
2. **Применение миграций**:
   ```bash
   make upgrade
   ```
3. Откат миграций:

    Если необходимо откатить последнюю миграцию, выполните:
    ```bash
    make downgrade
    ```

4. Остановка контейнеров Docker :

    Чтобы остановить контейнеры, выполните:
    ```bash
    make down
    ```
___
⭐ Не забудьте поставить звезду, если этот шаблон вам помог!