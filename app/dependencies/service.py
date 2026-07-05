from starlette import status

from app.services import (
    EvaluationService,
    MeetingService,
    TaskService,
    TaskCommentService,
    TeamService,
    UserService,
    BaseService,
)
from app.repository import (
    EvaluationRepository,
    MeetingRepository,
    TaskRepository,
    TaskCommentRepository,
    TeamRepository,
    UserRepository,
    BaseRepository,
)
from fastapi import Body, HTTPException
from app.schemas import ServiceName
from app.utils.enums_service import ServiceTypeEnum


def get_service(service_name: ServiceName = Body()) -> BaseService:
    service_map = {
        ServiceTypeEnum.evaluation: (EvaluationService, EvaluationRepository),
        ServiceTypeEnum.meeting: (MeetingService, MeetingRepository),
        ServiceTypeEnum.task: (TaskService, TaskRepository),
        ServiceTypeEnum.task_comment: (
            TaskCommentService,
            TaskCommentRepository,
        ),  # 1  2 - meeting_partipints
        ServiceTypeEnum.team: (TeamService, TeamRepository),
        ServiceTypeEnum.user: (UserService, UserRepository),
    }

    service_map_result: tuple[BaseService, BaseRepository] = service_map.get(
        service_name.name
    )
    if service_map_result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Not found service '{service_name}'",
        )
    service, repository = service_map_result
    return service(repository())
