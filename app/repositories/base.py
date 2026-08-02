from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base


class BaseRepository[ModelType: Base]:
    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get_by_id(self, db: AsyncSession, id: Any) -> ModelType | None:
        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        query = select(self.model).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj_in: dict[str, Any]) -> ModelType:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: ModelType, obj_in: dict[str, Any]
    ) -> ModelType:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: Any) -> bool:
        db_obj = await self.get_by_id(db, id)
        if not db_obj:
            return False

        await db.delete(db_obj)
        await db.commit()
        return True
