from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from ..utils.db_errors import parse_integrity_error
from ..config.response import ResponseFactory
from sqlalchemy.exc import IntegrityError, DataError
import logging

logger = logging.getLogger(__name__)

bms_app = FastAPI(title="BMS")


def setup_exception_handlers(app: FastAPI):

    # DEVELOPMENT добавить обработчик ошибок связанных с БД post едит ПРОДОЛЖИТЬ ТУТ. Решить вопрос с ошибками в пост и патч запросах при обновлении уникальных полей либо вводе значений внешних ключей, которых не существует.

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        # Логируем полную ошибку для разработчиков
        logger.exception(f"IntegrityError on {request.method} {request.url}")

        # Парсим ошибку
        status_code, errors = parse_integrity_error(exc)

        return JSONResponse(
            status_code=status_code,
            content=ResponseFactory.error(
                message="Constraint violation", errors=[errors]
            ).model_dump(),
        )

    @app.exception_handler(DataError)
    async def data_error_handler(request: Request, exc: DataError):
        logger.exception(f"DataError on {request.method} {request.url}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "detail": "Invalid data",
                "errors": {"__all__": "Некорректные данные"},
            },
        )

    @app.exception_handler(Exception)
    async def catch_all_exceptions_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ResponseFactory.error(
                message=f"Somthing wrong...exception:{exc.args}"  # DEVELOPMENT remove exception
            ).model_dump(),
        )
