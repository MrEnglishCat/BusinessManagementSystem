from fastapi import APIRouter, Depends, Path, status
from ....config.response import BaseResponse, ResponseFactory
from ....utils.enums_service import ServiceTypeEnum
from ....schemas import UserCreateSchema, UserBaseSchema
from ....config.db import get_async_session
from ....services import BaseService
from ....dependencies.service import get_service_dependency
from sqlalchemy.ext.asyncio import AsyncSession

users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def get_users(
    session: AsyncSession = Depends(get_async_session),
    user_service: BaseService = Depends(get_service_dependency(ServiceTypeEnum.USER)),
):
    users = await user_service.get_all(session=session)
    return ResponseFactory.ok(data=users)


@users_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=BaseResponse,
)
async def post_users(
    user: UserCreateSchema,
    session: AsyncSession = Depends(get_async_session),
    user_service: BaseService = Depends(get_service_dependency(ServiceTypeEnum.USER)),
):
    update_result = await user_service.add(session=session, **user.model_dump())
    if update_result:
        return ResponseFactory.ok(data=update_result)
    return ResponseFactory.error(message="Error creating user")


@users_router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def get_user_by_id(
    user_id: int = Path(),
    session: AsyncSession = Depends(get_async_session),
    user_service: BaseService = Depends(get_service_dependency(ServiceTypeEnum.USER)),
):
    user = await user_service.get_one(session=session, id=user_id)
    if user:
        return ResponseFactory.ok(data=user)
    return ResponseFactory.error(message=f"User is not found")


@users_router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def delete_user_by_id(
    user_id: int = Path(),
    session: AsyncSession = Depends(get_async_session),
    user_service: BaseService = Depends(get_service_dependency(ServiceTypeEnum.USER)),
):
    delete_user = await user_service.delete(session=session, id=user_id)
    if delete_user:
        return ResponseFactory.ok(data=delete_user)
    return ResponseFactory.error(message="User is not found")


@users_router.patch("/{user_id}")
async def patch_user_by_id(
    user: UserBaseSchema,
    user_id: int = Path(),
    session: AsyncSession = Depends(get_async_session),
    user_service: BaseService = Depends(get_service_dependency(ServiceTypeEnum.USER)),
):
    update_user = await user_service.update(
        session=session, id=user_id, **user.model_dump()
    )
    if update_user:
        return ResponseFactory.ok(data=update_user)
    return ResponseFactory.error(message="User is not found")
