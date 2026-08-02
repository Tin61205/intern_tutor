# app/core/security.py
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

# Import settings để lấy các hằng số bảo mật
from app.core.config import settings

# Khởi tạo CryptContext, chỉ định dùng thuật toán bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordHasher:
    """
    Lớp tiện ích đóng gói logic xử lý mật khẩu.
    Sử dụng staticmethod để gọi thẳng mà không cần khởi tạo object.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Nhận vào mật khẩu gốc (plain password), trả về chuỗi đã bị băm (hashed).
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        So sánh mật khẩu gốc do user nhập với chuỗi hash trong DB.
        Trả về True nếu khớp, False nếu sai.
        """
        return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Tạo ra một chuỗi JWT chứa dữ liệu (data).
    Thường data sẽ là {"sub": "user_email@gmail.com"}
    """
    to_encode = data.copy()

    # Tính thời điểm token hết hạn (hiện tại + số phút)
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # Mã hóa thành chuỗi JWT
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """
    Giải mã chuỗi JWT để lấy lại data ban đầu.
    Nếu token hết hạn hoặc sai SECRET_KEY, sẽ trả về None.
    """
    try:
        decoded_jwt = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return decoded_jwt
    except JWTError:
        return None
