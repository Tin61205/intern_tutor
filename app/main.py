# app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lấy tên App từ file config
    print(f"🚀 {settings.APP_NAME} is starting up...")
    yield
    print(f"🛑 {settings.APP_NAME} is shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Task Management API",
    version="1.0.0",
    lifespan=lifespan,
)

# Gắn prefix API version 1 từ config
app.include_router(api_router, prefix=settings.API_V1_STR)


# Health Check Endpoint
@app.get("/", tags=["Root"])
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}", "docs_url": "/docs"}
