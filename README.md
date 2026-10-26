# FastAPI Backend Template

Стартовый шаблон backend-приложения на FastAPI с DDD-разделением, асинхронным SQLAlchemy и отзываемыми JWT-сессиями.

## Возможности

- FastAPI + async/await, версионированный API `/api/v1`
- Слои `domain`, `application`, `infrastructure`, `presentation`
- PostgreSQL + async SQLAlchemy 2.x + async Alembic
- Redis-сессии: JWT access-токен с `jti` можно отозвать досрочно
- Argon2id-хеширование паролей с отдельным pepper
- HttpOnly cookie, CORS с явным списком origins, health-check endpoints
- Redis rate limiting для login/register по IP + username
- Регистрация, вход, выход, `/me`, смена пароля и деактивация аккаунта
- Startup-миграции под PostgreSQL advisory lock (безопасно для нескольких реплик)
- Swagger/OpenAPI с описанием запросов, ответов и примеров ошибок
- Ruff, mypy, pytest и GitHub Actions CI
- Docker Compose для PostgreSQL и Redis

## Запуск

```bash
cp .env.example .env
poetry install
make up
make start
```

Приложение: `http://localhost:8000`, документация: `http://localhost:8000/api/docs`.
Swagger содержит описания эндпоинтов, схем, кодов ошибок и примеры ответов.

Миграции применяются автоматически при старте приложения. Вручную: `make upgrade`.

## API

| Метод | Путь | Описание |
| --- | --- | --- |
| `POST` | `/api/v1/users/register` | Регистрация |
| `POST` | `/api/v1/auth/login` | Вход, устанавливает HttpOnly cookie |
| `POST` | `/api/v1/auth/logout` | Выход и отзыв текущей сессии |
| `GET` | `/api/v1/auth/me` | Текущий пользователь |
| `POST` | `/api/v1/auth/change-password` | Смена пароля и отзыв всех сессий |
| `POST` | `/api/v1/auth/deactivate` | Деактивация аккаунта и отзыв всех сессий |
| `GET` | `/health/live` | Liveness probe |
| `GET` | `/health/ready` | Проверка PostgreSQL и Redis |

Для защищённых запросов используется cookie `APP_AUTH_COOKIE_NAME` (по умолчанию `authorization`).

## Структура

```text
.
├── migrations/                 # async Alembic
├── src/
│   ├── application/            # use cases, DTO, UnitOfWork protocol
│   ├── common/                 # конфигурация, исключения, логирование
│   ├── di/                     # единый composition root
│   ├── domains/                # entities, value objects, protocols
│   ├── infrastructure/         # SQLAlchemy, Redis, JWT, Argon2
│   ├── presentation/           # FastAPI-роутеры и Pydantic-схемы
│   ├── main.py                 # создание приложения и lifespan
│   └── routers.py              # регистрация API-роутеров
└── tests/                      # unit/API-тесты
```

## Команды

```bash
make lint        # ruff
make typecheck   # mypy
make test        # pytest
make migrate NAME="add something"  # новая миграция
```

## Безопасность

- `JWT_SECRET_KEY` и `PASSWORD_PEPPER` обязательны для production и не могут содержать примерные значения.
- В production используйте `APP_COOKIE_SECURE=True` и строгий список `APP_CORS_ORIGINS`.
- Cookie `HttpOnly`; `SameSite` настраивается через `APP_COOKIE_SAMESITE`.
- Срок жизни access-токена и серверной сессии синхронизирован.
- Обновление пароля и деактивация отзывают все сессии пользователя через Redis.
- Login/register ограничены по IP + username; при недоступности Redis запросы отклоняются fail-closed.
- Лимиты настраиваются через `RATE_LIMIT_LOGIN_*` и `RATE_LIMIT_REGISTER_*`.
