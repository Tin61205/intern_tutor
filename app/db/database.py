# app/db/database.py
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# 1. Tạo AsyncEngine
# future=True: Sử dụng style mới của SQLAlchemy 2.x
# echo=True: Print các câu SQL ra terminal (rất hữu ích để học và debug ở dev)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True,
)
# 2. Tạo Session Factory
# expire_on_commit=False: Giữ lại data của object sau khi commit, để có thể đọc tiếp mà không cần query lại
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# 3. Tạo Dependency get_db
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Hàm này sẽ được FastAPI gọi mỗi khi có một request cần tới Database.
    'async with' đảm bảo session luôn được tự động đóng (close) khi xong việc.
    """
    async with AsyncSessionLocal() as session:
        yield session
