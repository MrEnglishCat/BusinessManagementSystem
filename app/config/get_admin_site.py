from crudadmin import CRUDAdmin, RedisConfig

from app.config.db import get_session
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

redis_config = RedisConfig(host="localhost", port=6379, db=0)
admin = CRUDAdmin(
    session=get_session,
    SECRET_KEY="your-secret-key",
    session_backend="redis",
    redis_config=redis_config,
    initial_admin={
        "username": "admin",
        "password": "admin",
    },
)
admin.add_view(
    model=UserModel,
    create_schema=UserCreateSchema,
    update_schema=UserBaseSchema,
    select_schema=UserResponseSchema,
    allowed_actions={"view", "create", "update", "delete"},
    display_field="full_name",
)
admin.add_view(
    model=TeamModel,
    create_schema=TeamBaseSchema,
    update_schema=TeamBaseSchema,
    select_schema=TeamResponseSchema,
    allowed_actions={"view", "create", "update", "delete"},
    display_field="name",
)
admin.add_view(
    model=TaskModel,
    create_schema=TaskBaseSchema,
    update_schema=TaskBaseSchema,
    select_schema=TaskResponseSchema,
    display_field="title",
)
admin.add_view(
    model=MeetingModel,
    create_schema=MeetingBaseSchema,
    update_schema=MeetingBaseSchema,
    select_schema=MeetingResponseSchema,
    display_field="title",
)
admin.add_view(
    model=EvaluationModel,
    create_schema=EvaluationBaseSchema,
    update_schema=EvaluationBaseSchema,
    select_schema=EvaluationResponseSchema,
    display_field="score",
)
admin.add_view(
    model=TaskCommentModel,
    create_schema=TaskCommentBaseSchema,
    update_schema=TaskCommentBaseSchema,
    select_schema=TaskCommentResponseSchema,
    display_field="score",
)
