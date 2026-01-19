# Dockerfile
FROM python:3.10-slim

# Системные зависимости для Pygame (рендеринг MiniGrid)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY analysis/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаём папку для логов
RUN mkdir -p logs

# Генерируем maze.json перед запуском тестов
RUN python generate_maze.py

# Запуск тестов
CMD ["pytest", "tests/", "-v", "-s"]