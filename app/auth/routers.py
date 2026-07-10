from fastapi import APIRouter
from app.auth.config import auth_backend, fastapi_users
from app.auth.schemas import UserCreate, UserRead

auth_router = APIRouter(prefix="/auth", tags=["auth"])

auth_router.include_router(
    fastapi_users.get_auth_router(auth_backend),
)

auth_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)

# ❌ НЕ подключаем — у вас уже есть:
# - get_reset_password_router()
# - get_verify_router()
# - get_users_router()
