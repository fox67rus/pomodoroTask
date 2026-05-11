# Pomodoro Task Tracker

Личные задачи, Kanban-доска и Pomodoro-таймер.

## Стек

- FastAPI, SQLAlchemy 2.0, Alembic
- SQLite для локальной разработки, PostgreSQL через Docker Compose
- Jinja2, HTMX, Tailwind CSS, Alpine.js, SortableJS
- pytest + FastAPI TestClient

## Быстрый запуск

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
python -m uvicorn main:app --reload
```

Приложение будет доступно на `http://127.0.0.1:8000`.

## Миграции

```bash
python -m alembic upgrade head
```

В режиме разработки приложение также создаёт таблицы при старте, чтобы MVP запускался без лишних шагов.

## Тесты

```bash
python -m pytest -q
```

## Публикация на GitHub

```bash
git init -b main
git remote add origin https://github.com/fox67rus/pomodoroTask.git
git add .
git commit -m "Initial Pomodoro Task Tracker MVP"
git push -u origin main
```

## Docker

```bash
docker compose up --build
```

Перед production-запуском замените `SECRET_KEY` и пароли PostgreSQL.

## Основные сценарии

1. Зарегистрироваться или войти.
2. Создать задачу на странице `Новая задача`.
3. Открыть Kanban и перетащить карточку между колонками.
4. Запустить Pomodoro для выбранной задачи.
5. Проверить статистику на Dashboard.
