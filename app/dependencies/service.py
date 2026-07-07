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
from app.utils.enums_service import ServiceTypeEnum


def get_service(service_name: ServiceTypeEnum) -> BaseService:
    service_map = {
        ServiceTypeEnum.EVALUATION: (EvaluationService, EvaluationRepository),
        ServiceTypeEnum.MEETING: (MeetingService, MeetingRepository),
        ServiceTypeEnum.TASK: (TaskService, TaskRepository),
        ServiceTypeEnum.TASK_COMMENT: (
            TaskCommentService,
            TaskCommentRepository,
        ),  # 1  2 - meeting_partipints
        ServiceTypeEnum.TEAM: (TeamService, TeamRepository),
        ServiceTypeEnum.USER: (UserService, UserRepository),
    }

    service_map_result: tuple[BaseService, BaseRepository] = service_map.get(
        service_name
    )
    if service_map_result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Not found service '{service_name}'",
        )
    service, repository = service_map_result
    return service(repository())


def get_service_dependency(service_name: ServiceTypeEnum):
    def _get_service():
        return get_service(service_name=service_name)

    return _get_service
