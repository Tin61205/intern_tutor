# app/models/user.py
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import UserRole
from app.models.base import Base


class User(Base):
    __tablename__ = "users"  # Tên bảng trong PostgreSQL

    # Mapped[int] báo cho Python biết đây là int
    # mapped_column map nó thành INTEGER và làm khóa chính
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )

    # Mapped[str | None] biểu thị cột này có thể null (Optional)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.USER)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # func.now() yêu cầu Database tự động lấy giờ hệ thống khi tạo record
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
