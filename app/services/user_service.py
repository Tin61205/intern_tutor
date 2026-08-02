# app/services/user_service.py
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user import user_repository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    @classmethod
    async def get_all(cls, db: AsyncSession, skip: int = 0, limit: int = 10):
        # Service không tự query, mà nhờ Repository làm việc đó
        return await user_repository.get_all(db, skip=skip, limit=limit)

    @classmethod
    async def get_by_id(cls, db: AsyncSession, user_id: int):
        user = await user_repository.get_by_id(db, id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy user")
        return user

    @classmethod
    async def create(cls, db: AsyncSession, user_in: UserCreate):
        # 1. Nghiệp vụ: Kiểm tra email trùng
        existing_user = await user_repository.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email đã được sử dụng")

        # 2. Xử lý dữ liệu
        user_data = user_in.model_dump()
        password = user_data.pop("password")  # Lấy password ra khỏi dict

        user_data["hashed_password"] = f"fake_hash_{password}"  # Fake mã hóa
        user_data["role"] = "user"
        user_data["is_active"] = True

        # 3. Nhờ Repository lưu vào DB
        return await user_repository.create(db, obj_in=user_data)

    @classmethod
    async def update(cls, db: AsyncSession, user_id: int, user_in: UserUpdate):
        # 1. Tìm user
        user = await user_repository.get_by_id(db, id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy user")

        # 2. Cập nhật data
        update_data = user_in.model_dump(exclude_unset=True)
        return await user_repository.update(db, db_obj=user, obj_in=update_data)

    @classmethod
    async def delete(cls, db: AsyncSession, user_id: int):
        success = await user_repository.delete(db, id=user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Không tìm thấy user")
        return True
    