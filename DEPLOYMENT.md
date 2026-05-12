# Deployment

Инструкция описывает деплой через GitHub Actions на сервер по SSH. Workflow собирает Docker-образ, публикует его в GitHub Container Registry и затем перезапускает сервис `web` на сервере.

## Что делает workflow

Файл `.github/workflows/deploy.yml` запускается при push в ветку `main` и состоит из двух job:

- `build`: собирает Docker-образ и публикует теги `latest` и `${{ github.sha }}` в GHCR.
- `deploy`: подключается к серверу по SSH, подтягивает `main`, скачивает собранный SHA-образ и перезапускает контейнер.

Папка проекта на сервере задана прямо в workflow:

```bash
/opt/apps/projects/pomodoro-task
```

Если нужен другой путь, измени переменную `PROJECT_DIR` в `.github/workflows/deploy.yml`.

## GitHub Secrets

Открой GitHub repository → `Settings` → `Secrets and variables` → `Actions` → `New repository secret` и добавь:

- `SSH_HOST`: IP или домен сервера.
- `SSH_USER`: пользователь на сервере, например `deploy` или `root`.
- `SSH_KEY`: приватный SSH-ключ без passphrase, у которого есть доступ к серверу.
- `SSH_PORT`: SSH-порт. Можно не добавлять, тогда используется `22`.

`GITHUB_TOKEN` создавать вручную не нужно. GitHub Actions предоставляет его автоматически.

## Подготовка сервера

На сервере должны быть установлены:

```bash
docker --version
docker compose version
git --version
```

Создай папку проекта и склонируй репозиторий:

```bash
sudo mkdir -p /opt/apps/projects/pomodoro-task
sudo chown -R $USER:$USER /opt/apps/projects/pomodoro-task
git clone https://github.com/fox67rus/pomodoroTask.git /opt/apps/projects/pomodoro-task
cd /opt/apps/projects/pomodoro-task
```

Проверь, что сервер может читать GitHub Container Registry:

```bash
docker login ghcr.io
```

Если пакет GHCR приватный, пользователю нужен доступ к репозиторию или token с правом `read:packages`.

## Переменные приложения

Production-секреты не хранятся в Git. `docker-compose.yml` читает их из `.env` на сервере.

Создай `.env` из примера:

```bash
cd /opt/apps/projects/pomodoro-task
cp .env.production.example .env
nano .env
```

Заполни реальные значения:

```env
APP_ENV=production
SECRET_KEY=replace-with-a-long-random-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=10080

POSTGRES_DB=task_tracker
POSTGRES_USER=task_tracker_user
POSTGRES_PASSWORD=replace-with-a-strong-database-password
```

`SECRET_KEY` и `POSTGRES_PASSWORD` должны быть уникальными сильными значениями. Файл `.env` уже добавлен в `.gitignore`, его нельзя коммитить.

## Первый запуск вручную

После подготовки сервера можно проверить запуск:

```bash
cd /opt/apps/projects/pomodoro-task
docker compose pull web
docker compose up -d
docker compose ps
docker compose logs --tail=50 web
```

## Автоматический деплой

После настройки secrets каждый push в `main` запустит:

1. Сборку и публикацию Docker-образа в GHCR.
2. SSH-деплой на сервер.
3. `docker compose pull web`.
4. `docker compose up -d --no-deps web`.

Проверить результат можно во вкладке GitHub `Actions`.
