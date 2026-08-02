# app/core/exceptions.py
from fastapi import HTTPException, status


class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy người dùng"
        )


class InvalidTokenException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"},
        )


class WrongCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )


class EmailAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email đã được sử dụng"
        )
