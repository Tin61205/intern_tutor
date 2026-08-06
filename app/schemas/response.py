# app/schemas/response.py
from typing import Any

from pydantic import BaseModel


class BaseResponse[T](BaseModel):
    """
    Response mẫu chuẩn (Standardized Response) để bọc toàn bộ API.
    """

    success: bool = True
    message: str = "Thành công"
    data: T | None = None
    error_code: str | None = None


class ErrorResponse(BaseModel):
    """
    Response dành riêng cho việc trả về lỗi.
    """

    success: bool = False
    message: str
    error_code: str
    data: Any | None = None
