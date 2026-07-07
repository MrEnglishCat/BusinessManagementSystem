from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from ..config.response import ResponseFactory


def setup_exception_handlers(app: FastAPI):

    @app.exception_handler(Exception)
    async def catch_all_exceptions_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=404,
            content=ResponseFactory.error(
                message=f"Somthing wrong...exception:{exc.args}"  # DEVELOPMENT remove exception
            ).model_dump(),
        )
