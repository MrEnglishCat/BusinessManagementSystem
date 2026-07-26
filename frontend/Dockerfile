# Frontend Dockerfile


FROM python:3.14

# Рабочая директория
WORKDIR /usr/src/app

# Копирование файлов фронтенда
COPY . .

# Expose port
EXPOSE 8080

# Запуск HTTP-сервера
CMD ["python", "-m", "http.server", "8080"]