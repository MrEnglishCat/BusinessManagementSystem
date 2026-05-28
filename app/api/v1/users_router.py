from fastapi import APIRouter

users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get("/")
async def get_users():
    return {"message": "Все оценки"}
