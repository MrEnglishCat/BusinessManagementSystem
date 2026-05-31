from fastapi import FastAPI
from app.api.v1.v1_router import v1_router

bms_app = FastAPI(title="Business Management System")
bms_app.include_router(v1_router)
