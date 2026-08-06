# app/db/database.py
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# 1. Tạo AsyncEngine
# future=True: Sử dụng style mới của SQLAlchemy 2.x
# echo=True: Print các câu SQL ra terminal (rất hữu ích để học và debug ở dev)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "dev",  # Chỉ in SQL ra màn hình khi ở môi trường dev
    future=True,
    pool_size=20,  # Số lượng connection tối đa giữ trong Pool
    max_overflow=10,  # Số lượng connection tạo thêm nếu Pool đầy
    pool_timeout=30,  # Thời gian chờ tối đa để mượn connection (giây)
    pool_pre_ping=True,  # Kiểm tra connection còn sống không trước khi mượn (tránh lỗi "MySQL has gone away")
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


async def close_db_connection():
    """Hàm đóng toàn bộ pool kết nối xuống DB một cách sạch sẽ (Graceful Shutdown)"""
    await engine.dispose()
