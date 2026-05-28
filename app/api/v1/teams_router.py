from fastapi import APIRouter

teams_router = APIRouter(prefix="/teams", tags=["teams"])


@teams_router.get("/")
async def get_teams():
    return {"message": "Все оценки"}
