# app/core/exceptions.py
from fastapi import status


class AppException(Exception):
    """Base class cho mọi lỗi tự định nghĩa trong ứng dụng."""

    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        headers: dict | None = None,
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.headers = headers


# --- CÁC LỖI GỐC (BASE EXCEPTIONS) ---
class AuthenticationException(AppException):
    def __init__(self, message: str = "Xác thực thất bại", headers: dict | None = None):
        if headers is None:
            headers = {"WWW-Authenticate": "Bearer"}
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
            message=message,
            headers=headers,
        )


class AuthorizationException(AppException):
    def __init__(self, message: str = "Bạn không có quyền truy cập"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
            message=message,
        )


class ResourceNotFoundException(AppException):
    def __init__(self, message: str = "Tài nguyên không tồn tại"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message=message,
        )


class BusinessException(AppException):
    def __init__(self, message: str = "Lỗi nghiệp vụ"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BAD_REQUEST",
            message=message,
        )


class ValidationException(AppException):
    def __init__(self, message: str = "Dữ liệu không hợp lệ"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            message=message,
        )


# --- CÁC LỖI CHI TIẾT KẾ THỪA TỪ LỖI GỐC ---
class UserNotFoundException(ResourceNotFoundException):
    def __init__(self):
        super().__init__(message="Không tìm thấy người dùng")


class InvalidTokenException(AuthenticationException):
    def __init__(self):
        super().__init__(message="Token không hợp lệ hoặc đã hết hạn")


class WrongCredentialsException(AuthenticationException):
    def __init__(self):
        super().__init__(message="Email hoặc mật khẩu không chính xác")


class EmailAlreadyExistsException(BusinessException):
    def __init__(self):
        super().__init__(message="Email đã được sử dụng")
