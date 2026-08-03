# app/main.py
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import setup_logging
from app.core.redis import RedisClient
from app.db.database import get_db
from app.middleware import RequestLoggingMiddleware
from app.schemas.response import ErrorResponse

# --- KHỞI ĐỘNG HỆ THỐNG LOGGING ---
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lấy tên App từ file config
    print(f"🚀 {settings.APP_NAME} is starting up...")
    
    # Khởi động kết nối Redis (Tạo Connection Pool)
    RedisClient.get_client()
    
    yield
    
    # Đóng toàn bộ kết nối Redis khi server tắt để giải phóng RAM
    await RedisClient.close()
    print(f"🛑 {settings.APP_NAME} is shutting down...")


# --- OPENAPI METADATA ---
tags_metadata = [
    {
        "name": "Authentication",
        "description": "API Xác thực người dùng (Đăng nhập, Đăng ký).",
    },
    {
        "name": "Users",
        "description": "Quản lý hồ sơ người dùng.",
    },
    {
        "name": "System",
        "description": "Kiểm tra trạng thái hệ thống.",
    },
]

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="""
    TaskHub API - Hệ thống quản lý công việc chuyên nghiệp.
    
    ## Tính năng cốt lõi:
    * **Xác thực**: JWT Token, Phân quyền RBAC.
    * **Tối ưu hóa**: Redis Caching siêu tốc.
    """,
    contact={
        "name": "TaskHub Support",
        "email": "support@taskhub.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=tags_metadata,
    lifespan=lifespan,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1} # Ẩn danh sách Model rườm rà dưới đáy Swagger
)

# Đăng ký Middleware (Lưu ý: Đăng ký càng sớm càng tốt để bao bọc toàn bộ App)
app.add_middleware(RequestLoggingMiddleware)

# Gắn prefix API version 1 từ config
app.include_router(api_router, prefix=settings.API_V1_STR)


# Root Endpoint
@app.get("/", tags=["System"])
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}", "docs_url": "/docs"}


# Định nghĩa Dependency an toàn (Tránh lỗi B008 của Ruff)
SessionDep = Annotated[AsyncSession, Depends(get_db)]

# Health Check Endpoint
@app.get("/health", tags=["System"])
async def health_check(db: SessionDep):
    """
    API dùng để kiểm tra sức khỏe của hệ thống.
    Hữu ích khi kết hợp với Docker, Kubernetes, AWS Target Group.
    """
    health_status = {
        "status": "healthy",
        "database": "disconnected",
        "redis": "disconnected"
    }
    
    # 1. Kiểm tra kết nối PostgreSQL
    try:
        # SELECT 1 là câu query nhẹ nhất để test DB
        await db.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except SQLAlchemyError:
        health_status["status"] = "unhealthy"
        health_status["database"] = "error"

    # 2. Kiểm tra kết nối Redis
    try:
        redis_client = RedisClient.get_client()
        # Hàm ping() trả về True nếu Redis đang sống
        if await redis_client.ping():
            health_status["redis"] = "connected"
    except RedisError:
        health_status["status"] = "unhealthy"
        health_status["redis"] = "error"
        
    return health_status


# --- GLOBAL EXCEPTION HANDLERS ---

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Bắt toàn bộ các lỗi Custom do chúng ta tự định nghĩa."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            message=exc.message,
            error_code=exc.error_code,
        ).model_dump(),
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Bắt lỗi Pydantic Validation (422) và chuẩn hóa format trả về."""
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            message="Dữ liệu đầu vào không hợp lệ",
            error_code="VALIDATION_ERROR",
            data=exc.errors(),
        ).model_dump(),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Bắt các lỗi HTTP mặc định của FastAPI (ví dụ 404 Not Found, 405 Method Not Allowed)."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            message=str(exc.detail),
            error_code="HTTP_EXCEPTION",
        ).model_dump(),
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Chốt chặn cuối cùng: Bắt tất cả các lỗi chưa được handle (500 Server Error)."""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message="Lỗi hệ thống nội bộ, vui lòng thử lại sau.",
            error_code="INTERNAL_SERVER_ERROR",
        ).model_dump(),
    )
