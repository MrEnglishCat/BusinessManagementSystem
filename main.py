from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.api.v1.v1_router import v1_router
from app.admin.setup import setup_admin
from app.config.response import ResponseFactory
from app.exceptions.exception_handlers import setup_exception_handlers
from app.auth.routers import auth_router

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
setup_exception_handlers(bms_app)

bms_app.include_router(v1_router)
bms_app.include_router(auth_router)

"""Управление договорами - Типы договоров - Редактирование типа. 

Сделать не кликабельными коды типов договоров. Так де как и некликабельно название договоров. 
"""
