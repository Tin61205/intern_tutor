# app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.redis import RedisClient
from app.middleware import RequestLoggingMiddleware
from app.schemas.response import ErrorResponse


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


# Health Check Endpoint
@app.get("/", tags=["System"])
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}", "docs_url": "/docs"}


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
