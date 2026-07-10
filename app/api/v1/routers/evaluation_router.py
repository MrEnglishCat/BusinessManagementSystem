from fastapi import APIRouter, Depends, Body, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from ....config.response import ResponseFactory, BaseResponse, ResponseError
from ....config.db import get_async_session
from ....schemas import EvaluationBaseSchema
from ....dependencies.service import get_service_dependency
from ....utils.enums_service import ServiceTypeEnum
from ....services import BaseService

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
):
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


@evaluation_router.patch("/{evaluation_id}")
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
