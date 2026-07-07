from fastapi import FastAPI

from ..config.db import async_engine_db, get_session

from app.models.evaluation import EvaluationModel
from app.models.meetings import MeetingModel
from app.models.tasks import TaskCommentModel, TaskModel
from app.models.teams import TeamModel
from app.models.users import UserModel
from app.schemas.evaluation import EvaluationBaseSchema, EvaluationResponseSchema
from app.schemas.meetings import MeetingBaseSchema, MeetingResponseSchema
from app.schemas.tasks import (
    TaskBaseSchema,
    TaskCommentBaseSchema,
    TaskCommentResponseSchema,
    TaskResponseSchema,
)
from app.schemas.teams import TeamBaseSchema, TeamResponseSchema
from app.schemas.users import UserBaseSchema, UserCreateSchema, UserResponseSchema

from starlette_admin.contrib.sqla import Admin
from .views import (
    UserView,
    TeamView,
    TaskCommentModelView,
    TaskModelView,
    MeetingModelView,
    EvaluationModelView,
)
from .admin_auth import WebAuthProvider


def setup_admin(app: FastAPI):
    admin = Admin(
        engine=async_engine_db, title="BMS", debug=True, auth_provider=WebAuthProvider()
    )
    admin.add_view(UserView(model=UserModel))
    admin.add_view(TeamView(model=TeamModel))
    admin.add_view(TaskCommentModelView(model=TaskCommentModel))
    admin.add_view(TaskModelView(model=TaskModel))
    admin.add_view(MeetingModelView(model=MeetingModel))
    admin.add_view(EvaluationModelView(model=EvaluationModel))

    admin.mount_to(app)
