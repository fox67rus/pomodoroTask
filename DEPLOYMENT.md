# Deployment

Инструкция описывает деплой через GitHub Actions на сервер по SSH. Workflow собирает Docker-образ, публикует его в GitHub Container Registry и затем перезапускает сервис `web` на сервере.

## Что делает workflow

Файл `.github/workflows/deploy.yml` запускается при push в ветку `main` и состоит из двух job:

- `build`: собирает Docker-образ и публикует теги `latest` и `${{ github.sha }}` в GHCR.
- `deploy`: подключается к серверу по SSH, подтягивает `main`, скачивает собранный SHA-образ и перезапускает контейнер.

Папка проекта на сервере задана прямо в workflow:

```bash
/opt/pomodoro-task
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
sudo mkdir -p /opt/pomodoro-task
sudo chown -R $USER:$USER /opt/pomodoro-task
git clone https://github.com/fox67rus/pomodoroTask.git /opt/pomodoro-task
cd /opt/pomodoro-task
```

Проверь, что сервер может читать GitHub Container Registry:

```bash
docker login ghcr.io
```

Если пакет GHCR приватный, пользователю нужен доступ к репозиторию или token с правом `read:packages`.

## Переменные приложения

Сейчас `docker-compose.yml` содержит production-переменные прямо в файле:

```yaml
SECRET_KEY: change-me
DATABASE_URL: postgresql+psycopg://postgres:postgres@db:5432/task_tracker
```

Перед реальным production-запуском замени `SECRET_KEY` и пароли PostgreSQL на безопасные значения. Лучше вынести их в `.env` на сервере и не хранить реальные секреты в Git.

## Первый запуск вручную

После подготовки сервера можно проверить запуск:

```bash
cd /opt/pomodoro-task
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
