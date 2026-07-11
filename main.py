from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.api.v1.v1_router import v1_router
from app.admin.setup import setup_admin
from app.exceptions.exception_handlers import setup_exception_handlers
from app.auth.routers import auth_router
from app.config.db import settings

bms_app = FastAPI(title="Business Management System")


bms_app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="session",
    max_age=86400 * 7,
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
