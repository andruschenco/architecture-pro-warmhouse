# Этап сборки
FROM python:3.11-slim AS builder

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir --user -r requirements.txt

# Этап выполнения
FROM python:3.11-slim

WORKDIR /app

# Копируем установленные зависимости
COPY --from=builder /root/.local /root/.local

# Копируем исходный код
COPY ./app ./app

# Добавляем путь к Python
ENV PATH=/root/.local/bin:$PATH \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

# Открываем порт
EXPOSE 8083

# Запускаем приложение
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8083"]