from fastapi import APIRouter, Body, HTTPException, status, Depends
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.db import get_session
from app.config.response import BaseResponse, ResponseFactory
from app.config.data_generator.generator import (
    run_generate,
)
from app.dependencies.service import get_service
from app.schemas import TaskCommentResponseSchema
from app.services import BaseService
from app.utils.enums_service import ServiceTypeEnum

generator_router = APIRouter(tags=["data_generator"])


@generator_router.post("/data_generate")
async def generate_data(
    session=Depends(get_session),
):
    import time

    start = time.monotonic()
    await asyncio.create_task(run_generate(session=session))
    return ResponseFactory.ok(message=f"Success. Time: {time.monotonic() - start}")


@generator_router.post(
    "/clear_tables",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def clear_tables(
    session: AsyncSession = Depends(get_session),
):
    service_list = [
        get_service(service_name=service_type) for service_type in ServiceTypeEnum
    ]
    print(*service_list, sep="\n")
    for service in service_list:
        rowcount = await service.delete_all(session=session)
        print(service, rowcount)

    return ResponseFactory.ok()
