from fastapi import APIRouter
from app.api.v1.data_generator_router import generator_router
from . import (
    evaluation_router,
    meeting_router,
    tasks_router,
    teams_router,
    users_router,
)

v1_router = APIRouter(
    prefix="/v1",
)

v1_router.include_router(evaluation_router)
v1_router.include_router(meeting_router)
v1_router.include_router(tasks_router)
v1_router.include_router(teams_router)
v1_router.include_router(users_router)
v1_router.include_router(generator_router)
