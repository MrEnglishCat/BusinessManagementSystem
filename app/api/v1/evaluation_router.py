from fastapi import APIRouter

evaluation_router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@evaluation_router.get("/")
async def get_evaluations():
    return {"message": "Все оценки"}
