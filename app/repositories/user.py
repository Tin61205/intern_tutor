# app/repositories/user.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self):
        # Kế thừa BaseRepository và truyền model User vào
        super().__init__(User)

    # Ngoài 5 hàm CRUD có sẵn, bạn có thể viết thêm các câu query ĐẶC THÙ ở đây
    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def create_user(self, db: AsyncSession, user_data: dict) -> User:
        """
        Lưu user mới vào Database.
        Tái sử dụng hàm create() từ BaseRepository.
        """
        return await self.create(db, obj_in=user_data)


# Khởi tạo object để import dùng ở nơi khác
user_repository = UserRepository()
