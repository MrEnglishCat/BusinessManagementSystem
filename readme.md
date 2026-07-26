git clone https://github.com/MrEnglishCat/BusinessManagementSystem.git

cd ./BusinessManagementSystem
python -r install requirements.txt


Открыть второй терминал в каталоге проекта ./BusinessManagementSystem

Выполнить команды ниже для запуска минимального фронтенда. 


cd ./frontend

python -m http.server 8080






http://localhost:8000/admin - страница админки

http://localhost:8080/#/login  - страница авторизации фронтенда


Есть ручки для генерации и очистки таблиц(is_superuser не удаляется, генерируется один раз.). Первая генерация возможна через ручки в swagger: http://127.0.0.1:8000/docs#/. 


Модель генерации superuser:

UserModel(
            email="admin@admin.admin",
            username="admin",
            hashed_password=passwd_hasher.hash("admin"),
            full_name="Системный Администратор",
            role=UserRole.ADMIN,
            is_active=True,
            is_superuser=True,
            team_id=None,
)

Ручка генерации данных:
http://127.0.0.1:8000/v1/mock_manager/data_generate
Есть payload:
{
    "users_count": 100,
    "teams_count": 20,
    "tasks_count": 200,
    "meetings_count": 50,
    "evaluations_count": 300,
    "comments_per_task_min": 2,
    "comments_per_task_max": 5
}

Ручка очистки таблиц. Superuser не удаляется. Payload нету.
http://127.0.0.1:8000/v1/mock_manager/clear_tables
