from fastapi import APIRouter

meeting_router = APIRouter(prefix="/meetings", tags=["meetings"])


@meeting_router.get("/")
async def meeting():
    return {"message": "Все оценки"}
