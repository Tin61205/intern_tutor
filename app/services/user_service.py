# app/services/user_service.py
from datetime import UTC, datetime

from app.schemas.user import UserCreate, UserUpdate
from fastapi import HTTPException

# Mock DB chuyển từ file router sang đây
FAKE_DB = []
CURRENT_ID = 1


class UserService:
    @classmethod
    def get_all(cls, skip: int = 0, limit: int = 10):
        return FAKE_DB[skip : skip + limit]

    @classmethod
    def get_by_id(cls, user_id: int):
        user = next((u for u in FAKE_DB if u["id"] == user_id), None)
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy user")
        return user

    @classmethod
    def create(cls, user_in: UserCreate):
        global CURRENT_ID
        if any(u["email"] == user_in.email for u in FAKE_DB):
            raise HTTPException(status_code=400, detail="Email đã được sử dụng")

        new_user = {
            "id": CURRENT_ID,
            "email": user_in.email,
            "full_name": user_in.full_name,
            "hashed_password": f"fake_hash_{user_in.password}",  # Đợi Session 3 sẽ dùng Passlib băm thật
            "role": "MEMBER",
            "is_active": True,
            "created_at": datetime.now(UTC),
        }
        FAKE_DB.append(new_user)
        CURRENT_ID += 1
        return new_user

    @classmethod
    def update(cls, user_id: int, user_in: UserUpdate):
        user_idx = next((i for i, u in enumerate(FAKE_DB) if u["id"] == user_id), None)
        if user_idx is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy user")

        update_data = user_in.model_dump(exclude_unset=True)
        FAKE_DB[user_idx].update(update_data)
        return FAKE_DB[user_idx]

    @classmethod
    def delete(cls, user_id: int):
        global FAKE_DB
        initial_len = len(FAKE_DB)
        FAKE_DB = [u for u in FAKE_DB if u["id"] != user_id]
        if len(FAKE_DB) == initial_len:
            raise HTTPException(status_code=404, detail="Không tìm thấy user")
        return True
