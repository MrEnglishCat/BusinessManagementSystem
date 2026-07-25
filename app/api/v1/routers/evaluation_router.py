from fastapi import APIRouter, Depends, Body, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from ....auth.config import current_active_user
from ....config.response import ResponseFactory, BaseResponse, ResponseError
from ....config.db import get_async_session
from ....schemas import EvaluationBaseSchema
from ....dependencies.service import get_service_dependency
from ....utils.enums_service import ServiceTypeEnum, UserRole
from ....services import BaseService
from ....models import UserModel

evaluation_router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


@evaluation_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def get_evaluations(
    session: AsyncSession = Depends(get_async_session),
    evaluation_service: BaseService = Depends(
        get_service_dependency(ServiceTypeEnum.EVALUATION)
    ),
):
    evaluations = await evaluation_service.get_all(session=session)
    if evaluations:
        return ResponseFactory.ok(data=evaluations)
    return ResponseFactory.error(message="Evaluation is not found")


@evaluation_router.post(
    "/average",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def get_average_evaluation_by_range(
    start_date: datetime = Body(),
    end_date: datetime = Body(),
    session: AsyncSession = Depends(get_async_session),
    evaluation_service: BaseService = Depends(
        get_service_dependency(ServiceTypeEnum.EVALUATION)
    ),
):
    average_evaluations = await evaluation_service.get_average_evaluation(
        session=session, start_date=start_date, end_date=end_date
    )
    if average_evaluations:
        return ResponseFactory.ok(data=average_evaluations)
    return ResponseFactory.error(message="Average evaluation is not found")


@evaluation_router.get(
    "/{evaluation_id}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def get_evaluation_by_id(
    evaluation_id: int = Path(),
    session: AsyncSession = Depends(get_async_session),
    evaluation_service: BaseService = Depends(
        get_service_dependency(ServiceTypeEnum.EVALUATION)
    ),
):
    evaluation = await evaluation_service.get_one(session=session, id=evaluation_id)
    if evaluation:
        return ResponseFactory(data=evaluation)
    return ResponseFactory.error(message="Evaluation is not found")


@evaluation_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=BaseResponse,
)
async def create_evaluations(
    evaluation: EvaluationBaseSchema = Body(),
    session: AsyncSession = Depends(get_async_session),
    evaluation_service: BaseService = Depends(
        get_service_dependency(ServiceTypeEnum.EVALUATION)
    ),
    current_user: UserModel = Depends(current_active_user),
):

    if current_user.role != UserRole.MANAGER:
        return ResponseFactory.error(
            message="Only users with the manager role can rate"
        )

    new_evaluation = await evaluation_service.add(
        session=session, **evaluation.model_dump()
    )
    return ResponseFactory.ok(data=new_evaluation)


@evaluation_router.delete(
    "/{evaluation_id}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def delete_evaluation_by_id(
    evaluation_id: int = Path(),
    session: AsyncSession = Depends(get_async_session),
    evaluation_service: BaseService = Depends(
        get_service_dependency(ServiceTypeEnum.EVALUATION)
    ),
):
    delete_result = await evaluation_service.delete(session=session, id=evaluation_id)
    if delete_result:
        return ResponseFactory.ok(data=delete_result)
    return ResponseFactory.error(message="Evaluation is not found")


@evaluation_router.patch(
    "/{evaluation_id}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def patch_team_by_id(
    evaluation: EvaluationBaseSchema,
    evaluation_id: int = Path(),
    session: AsyncSession = Depends(get_async_session),
    evaluation_service: BaseService = Depends(
        get_service_dependency(ServiceTypeEnum.EVALUATION)
    ),
):
    update_evaluation = await evaluation_service.update(
        session=session, id=evaluation_id, **evaluation.model_dump()
    )
    if update_evaluation:
        return ResponseFactory.ok(data=update_evaluation)
    return ResponseFactory.error(message="Meeting is not found")
