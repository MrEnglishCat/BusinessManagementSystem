from fastapi import APIRouter

meeting_router = APIRouter(prefix="/meetings", tags=["Meeting"])


@meeting_router.get("/")
async def get_meetings():
    return {"message": "Все оценки"}


@meeting_router.get("/{meeting_id}")
async def get_meetings_by_id(meeting_id):
    return {"message": "Все оценки"}


@meeting_router.post("/")
async def post_meetings():
    return {"message": "Все оценки"}


@meeting_router.delete("/{meeting_id}")
async def delete_meetings_by_id(meeting_id: int):
    return {"message": "Все оценки"}
