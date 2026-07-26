from fastapi import APIRouter, status, Depends, HTTPException
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.db import get_async_session
from app.config.response import BaseResponse, ResponseFactory
from app.config.data_generator.generator import (
    run_generate,
)
from app.dependencies.service import get_service
from app.utils.enums_service import ServiceTypeEnum
import time
from app.schemas.data_generator import GenerateDataRequest

generator_router = APIRouter(prefix="/mock_manager", tags=["Data generator"])


@generator_router.post("/data_generate")
async def generate_data(
    request: GenerateDataRequest = GenerateDataRequest(),
    session: AsyncSession = Depends(get_async_session),
):
    start = time.monotonic()

    # 🔥 Передаем кастомные значения или используем дефолты из settings
    await asyncio.create_task(
        run_generate(
            session=session,
            users_count=request.users_count,
            teams_count=request.teams_count,
            tasks_count=request.tasks_count,
            meetings_count=request.meetings_count,
            evaluations_count=request.evaluations_count,
            comments_per_task_min=request.comments_per_task_min,
            comments_per_task_max=request.comments_per_task_max,
        )
    )

    return ResponseFactory.ok(message=f"Success. Time: {time.monotonic() - start:.2f}s")


@generator_router.post(
    "/clear_tables",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def clear_tables(
    session: AsyncSession = Depends(get_async_session),
):

    services_to_clear = [
        ServiceTypeEnum.TASK_COMMENT,
        ServiceTypeEnum.EVALUATION,
        # ServiceTypeEnum.INVITE,
        ServiceTypeEnum.MEETING,
        ServiceTypeEnum.TASK,
        ServiceTypeEnum.TEAM,
        ServiceTypeEnum.USER,
    ]

    try:
        for service_type in services_to_clear:
            service = get_service(service_name=service_type)
            if service_type == ServiceTypeEnum.USER:
                rowcount = await service.bulk_delete(session=session)
            else:
                rowcount = await service.delete_all(session=session)
            print(f"✅ Очищено {service_type.value}: удалено {rowcount} записей")

        # Фиксируем все изменения в базе данных одной транзакцией
        await session.commit()

    except Exception as e:
        await session.rollback()
        print(f"❌ Ошибка при очистке таблиц: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка очистки базы данных: {str(e)}",
        )

    return ResponseFactory.ok(
        message="Все таблицы (кроме пользователей) успешно очищены"
    )
