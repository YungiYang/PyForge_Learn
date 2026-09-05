FROM python:3.12-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода приложения
COPY . .

# Экспорт порта
EXPOSE 8000

# Запуск приложения
CMD ["python", "run.py"]
