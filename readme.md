
# 🏢 Business Management System

[![Python](https://img.shields.io/badge/Python-3.14+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Полнофункциональная система управления бизнес-процессами с интуитивным интерфейсом и мощным API.

---

##  Содержание

- [Быстрый старт](#-быстрый-старт)
- [Доступ к приложению](#-доступ-к-приложению)
- [Учетная запись](#-учетная-запись)
- [Управление данными](#-управление-данными)
- [Функционал](#-функционал)
- [Галерея](#-галерея)
- [API Документация](#-api-документация)

---

##  Быстрый старт



### 1. Установка

```bash
# Клонирование репозитория
git clone https://github.com/MrEnglishCat/BusinessManagementSystem.git

# Переход в директорию проекта
cd ./BusinessManagementSystem

# Docker
docker compose up --build


# Последующие команды запуска, для запуска без докера.
# создание .venv
python -m venv .venv

# активация .venv Windows
.venv\Scripts\activate.bat

# активация .venv Linux
source .venv/bin/activate

# Установка зависимостей
python -m pip install -r requirements.txt
```

### 2. Запуск бэкенда

Запустите сервер FastAPI (порт 8000):

```bash
# Пример для uvicorn (рекомендуется)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Запуск фронтенда

**Откройте новый терминал** и выполните:

```bash
cd ./frontend

# Запуск HTTP-сервера на порту 8080
python -m http.server 8080
```

---

## 🌐 Доступ к приложению

| Интерфейс | URL | Описание |
|-----------|-----|----------|
| ️ **Фронтенд** | http://localhost:8080/#/login | Страница авторизации |
| ️ **Админка** | http://localhost:8000/admin | Панель администратора |
| 📖 **API Docs** | http://127.0.0.1:8000/docs#/ | Swagger (OpenAPI) |

---

## 👤 Учетная запись

После первой генерации данных (через swagger: /v1/mock_manager/data_generate) создается аккаунт суперпользователя(генерация данных около 15-20с):

| Параметр | Значение |
|----------|----------|
| **Username** | `admin` |
| **Email** | `admin@admin.admin` |
| **Password** | `admin` |
| **Роль** | `ADMIN` (Superuser) |

> ⚠️ **Важно:** Superuser не удаляется при очистке базы данных.

---

## 📊 Управление данными

### Генерация тестовых данных

**Первая генерация** доступна через Swagger UI.

**Эндпоинт:** `POST /v1/mock_manager/data_generate`

**Параметры запроса:**

```json
{
    "users_count": 100,
    "teams_count": 20,
    "tasks_count": 200,
    "meetings_count": 50,
    "evaluations_count": 300,
    "comments_per_task_min": 2,
    "comments_per_task_max": 5
}
```

### Очистка данных

**Эндпоинт:** `POST /v1/mock_manager/clear_tables`

- ✅ Superuser сохраняется
- ✅ Все остальные данные удаляются
- ✅ Payload не требуется

---

## ✨ Функционал

### Основные модули

- 👥 **Users** — управление пользователями и ролями
- ‍👩‍👧‍👦 **Teams** — создание команд и управление участниками
- 📋 **Tasks** — задачи с дедлайнами, статусами и комментариями
- 🤝 **Meetings** — планирование встреч с участниками
- ⭐ **Evaluations** — система оценки сотрудников
- 📅 **Calendar** — календарь событий с фильтрацией
- 📊 **Dashboard** — панель управления с аналитикой

### Возможности

- ✅ Гибкая система прав доступа (User, Manager, Admin)
- ✅ Каскадное управление связями (команды → пользователи → задачи)
- ✅ Временные метки и аудит действий
- ✅ RESTful API с автоматической документацией
- ✅ Генерация реалистичных тестовых данных

---

## 🖼️ Галерея

### 📊 Dashboard
![Dashboard](./readme_images/image.png)

### 📅 Calendar
![Calendar 1](./readme_images/image-1.png)
![Calendar 2](./readme_images/image-2.png)
![Calendar 3](./readme_images/image-3.png)
![Calendar 4](./readme_images/image-4.png)
![Calendar 5](./readme_images/image-5.png)

### 👥 Users
![Users 1](./readme_images/image-6.png)
![Users 2](./readme_images/image-7.png)

### 👨‍👩‍👧‍👦 Teams
![Teams 1](./readme_images/image-8.png)
![Teams 2](./readme_images/image-9.png)
![Teams 3](./readme_images/image-10.png)
![Teams 4](./readme_images/image-11.png)

### 📋 Tasks
![Tasks 1](./readme_images/image-12.png)
![Tasks 2](./readme_images/image-13.png)
![Tasks 3](./readme_images/image-14.png)

### 🤝 Meetings
![Meetings 1](./readme_images/image-15.png)
![Meetings 2](./readme_images/image-16.png)
![Meetings 3](./readme_images/image-17.png)
![Meetings 4](./readme_images/image-19.png)

### ⭐ Evaluations
![Evaluations 1](./readme_images/image-20.png)
![Evaluations 2](./readme_images/image-21.png)

---

## 📚 API Документация

Полная интерактивная документация доступна по адресу:

🔗 **http://127.0.0.1:8000/docs#/**

---

## 🛠️ Технологии

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL
- **Frontend:** Vanilla JavaScript, HTML5, CSS3 
- **Authentication:** JWT tokens
- **API Documentation:** Swagger UI (OpenAPI 3.0)

---

## 📄 Лицензия

MIT License — см. файл [LICENSE](LICENSE) для подробностей.

---

## 👨‍💻 Разработчик

**MrEnglishCat**  
GitHub: [@MrEnglishCat](https://github.com/MrEnglishCat)

---

<div align="center">

**⭐ Если вам понравился проект, поставьте звезду на GitHub!**

</div>
