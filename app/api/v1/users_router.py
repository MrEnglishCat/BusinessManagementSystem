from fastapi import APIRouter

users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get("/")
async def get_users():
    return {"message": "Все оценки"}


@users_router.post("/")
async def post_users():
    return {"message": "Все оценки"}


@users_router.get("/{user_id}")
async def get_users_by_id(user_id: int):
    return {"message": "Все оценки"}


@users_router("/{user_id}")
async def delete_users_by_id(user_id: int):
    return {"message": "Все оценки"}
