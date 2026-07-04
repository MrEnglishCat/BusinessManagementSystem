from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.v1_router import v1_router

# Настройка Redis
from contextlib import asynccontextmanager
from app.config.get_admin_site import admin


@asynccontextmanager
async def lifespan_app(app: FastAPI):
    await admin.initialize()
    yield


bms_app = FastAPI(title="Business Management System", lifespan=lifespan_app, debug=True)


bms_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


bms_app.mount("/admin", admin.app, "Admin")
bms_app.include_router(v1_router)

"""Управление договорами - Типы договоров - Редактирование типа. 

Сделать не кликабельными коды типов договоров. Так де как и некликабельно название договоров. 
"""
