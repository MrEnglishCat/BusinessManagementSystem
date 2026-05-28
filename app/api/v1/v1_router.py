from fastapi import APIRouter
from app.api.v1.evaluation_router import evaluation_router
from app.api.v1.meetings_router import meeting_router
from app.api.v1.tasks_router import tasks_router
from app.api.v1.teams_router import teams_router
from app.api.v1.users_router import users_router

v1_router = APIRouter(
    prefix="/v1",
)

v1_router.include_router(evaluation_router)
v1_router.include_router(meeting_router)
v1_router.include_router(tasks_router)
v1_router.include_router(teams_router)
v1_router.include_router(users_router)
