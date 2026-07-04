from fastapi import APIRouter, Body, HTTPException, status, Depends
import asyncio
from pydantic import BaseModel
from app.config.db import get_session
from app.config.response import ResponseFactory
from app.config.data_generator.generator import (
    run_generate,
)

generator_router = APIRouter(tags=["data_generator"])


class GeneratorScheme(BaseModel):
    name: str


@generator_router.post("/data_generate")
async def generate_data(
    session=Depends(get_session),
):
    import time

    start = time.monotonic()
    await asyncio.create_task(run_generate(session=session))
    return ResponseFactory.ok(message=f"Success. Time: {time.monotonic() - start}")


@generator_router.post("/clear_tables")
async def clear_tables(session=Depends(get_session)):

    return ResponseFactory.ok()
