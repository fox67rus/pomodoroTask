# ТЗ: Таск-трекер с Kanban-доской и Pomodoro-таймером

**Тип проекта**: Учебный / Портфолио  
**Стек**: FastAPI + SQLAlchemy 2.0 + HTMX + Tailwind CSS  
**Уровень**: Intermediate / Advanced

## Цель проекта
Создать современное веб-приложение для управления личными задачами с визуальной Kanban-доской и встроенным Pomodoro-таймером для повышения продуктивности.

---

## Используемый стек технологий

- **Backend**: FastAPI (Python 3.11+), Uvicorn
- **БД**: SQLAlchemy 2.0 + Alembic, PostgreSQL (в dev — SQLite)
- **Аутентификация**: fastapi-users (JWT + HTTPOnly cookies)
- **Валидация**: Pydantic v2
- **Frontend**: HTMX + Tailwind CSS + Alpine.js + SortableJS
- **Шаблонизатор**: Jinja2
- **Тестирование**: pytest + httpx
- **Деплой**: Docker + docker-compose (опционально)

---

## Этапы разработки

### Этап 1: Подготовка проекта (1–2 дня)

- Создание структуры проекта
- Настройка виртуального окружения и `requirements.txt`
- Подключение FastAPI + SQLAlchemy + Alembic
- Настройка `.env`, CORS, статических файлов и шаблонов
- Первая миграция БД
- Запуск приложения + Swagger UI (`/docs`)

**Результат**: рабочее пустое FastAPI-приложение с БД.

---

### Этап 2: MVP (7–10 дней)

#### 2.1 Аутентификация
- Регистрация, логин, logout
- Защищённые маршруты (`Depends(get_current_user)`)
- Работа с текущим пользователем

#### 2.2 Модель Task и CRUD
**Поля задачи**:
- `id`, `title`, `description`
- `status`: To Do, In Progress, Done
- `priority`: Low, Medium, High
- `deadline` (datetime)
- `tags` (JSON или отдельная таблица)
- `created_at`, `updated_at`
- `user_id`

- Полноценный CRUD (API + HTML-страницы)

#### 2.3 Kanban-доска (главная страница)
- Три колонки: **To Do | In Progress | Done**
- Drag & Drop с помощью SortableJS + HTMX
- Автоматическое обновление статуса в БД
- Красивые карточки задач

#### 2.4 Pomodoro-таймер
- Выбор задачи → запуск таймера
- Циклы: 25 мин работа / 5 мин перерыв / 15 мин длинный перерыв
- Сохранение помодоро-сессий в БД
- Пауза, сброс, звуковое оповещение

#### 2.5 Dashboard
- Сегодняшние и просроченные задачи
- Краткая статистика (выполнено задач, помодоро за день)
- Быстрый запуск Pomodoro

**Результат MVP**: полностью рабочее приложение.

---

### Этап 3: Nice-to-have (по приоритету)

#### 3.1 Расширение задач
- Подзадачи (subtasks)
- Комментарии
- Цветные метки / проекты

#### 3.2 Множественные проекты
- Модель `Project`
- Задачи привязаны к проекту
- Переключение между проектами

#### 3.3 Улучшения UI/UX
- Тёмная тема
- Поиск и расширенные фильтры
- Адаптивная верстка
- Красивые иконки (Heroicons / Lucide)

#### 3.4 Аналитика и статистика
- Графики (Chart.js)
- Помодоро по дням / неделям
- Тепловая карта продуктивности

#### 3.5 Продвинутый Pomodoro
- История сессий
- Настраиваемые длительности
- Уведомления браузера

#### 3.6 Дополнительно
- WebSocket (обновления в реальном времени)
- Экспорт в CSV/JSON
- Архив задач
- Soft delete

---

### Этап 4: Production & Полировка (2–4 дня)

- Docker + docker-compose (PostgreSQL + Redis)
- Environment variables
- Rate limiting, логирование
- Автоматические тесты
- Полная документация (Swagger + README)
- Деплой на Railway / Render / Fly.io

---

## Рекомендуемая структура проекта

```bash
task_tracker/
├── app/
│   ├── core/           # config, db, dependencies, security
│   ├── models/         # SQLAlchemy модели
│   ├── schemas/        # Pydantic схемы
│   ├── crud/           # бизнес-логика
│   ├── routers/        # api и html роутеры
│   ├── templates/      # HTML + Jinja2
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── utils/
├── migrations/
├── tests/
├── alembic.ini
├── main.py
├── requirements.txt
├── .env.example
└── Dockerfile