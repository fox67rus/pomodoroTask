# Легковесный базовый образ Python для запуска FastAPI-приложения.
FROM python:3.12-slim

# Не создаём .pyc-файлы и сразу выводим логи в stdout/stderr.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Все дальнейшие команды выполняются внутри /app.
WORKDIR /app

# Сначала копируем зависимости отдельно, чтобы Docker мог кешировать этот слой.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения в контейнер.
COPY . .

# Приложение слушает порт 8000 внутри контейнера.
EXPOSE 8000

# Запускаем FastAPI через Uvicorn и принимаем подключения извне контейнера.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
