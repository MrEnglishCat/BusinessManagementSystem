from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.v1_router import v1_router

# Настройка Redis
from contextlib import asynccontextmanager
from app.admin.setup import setup_admin
from starlette.middleware.sessions import SessionMiddleware

bms_app = FastAPI(title="Business Management System")
bms_app.add_middleware(
    SessionMiddleware,
    secret_key="your-very-secret-key-change-in-production",  # используйте переменную окружения
    session_cookie="session",  # имя cookie
    max_age=86400 * 7,  # время жизни сессии в секундах (7 дней)
)
bms_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
setup_admin(bms_app)
bms_app.include_router(v1_router)

"""Управление договорами - Типы договоров - Редактирование типа. 

Сделать не кликабельными коды типов договоров. Так де как и некликабельно название договоров. 
"""
