# tests/conftest.py
import os

# Ép buộc hệ thống load file .env.test trước khi bất kỳ file code nào được nạp
os.environ["ENVIRONMENT"] = "test"

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.db.database import get_db
from app.main import app
from app.models.base import Base


# ============================================================
# FIXTURE: Mock Redis Cache
# ============================================================
# Nguyên nhân lỗi "Event loop is closed":
# Khi UserService gọi cache.get/set/delete, nó cố kết nối Redis.
# Redis không chạy trong môi trường test → timeout → khi cleanup
# connection, event loop đã đóng → RuntimeError.
#
# Giải pháp: Thay thế cache bằng hàm giả (mock) trả kết quả ngay.
# Fixture này được inject vào db_session, nên mọi test dùng DB
# đều tự động được mock mà không cần khai báo thêm gì.
# ============================================================
@pytest.fixture()
def _mock_redis_cache(monkeypatch):
    """Mock toàn bộ Redis Cache để tránh lỗi Event Loop trong test."""

    async def fake_get(key):
        return None

    async def fake_set(key, value, ttl=None):
        return True

    async def fake_delete(key):
        return 1

    from app.core.cache import cache

    monkeypatch.setattr(cache, "get", fake_get)
    monkeypatch.setattr(cache, "set", fake_set)
    monkeypatch.setattr(cache, "delete", fake_delete)


# ============================================================
# FIXTURE: Setup Test Database (chạy 1 lần cho toàn bộ session)
# ============================================================
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """
    Chạy 1 lần duy nhất khi bắt đầu test session.
    Tạo toàn bộ cấu trúc bảng vào Test DB.
    """
    engine = create_async_engine(settings.DATABASE_URL, echo=False, poolclass=NullPool)
    async with engine.begin() as conn:
        # Dọn dẹp tàn dư từ các lần test trước (nếu có)
        await conn.run_sync(Base.metadata.drop_all)
        # Tạo bảng mới tinh
        await conn.run_sync(Base.metadata.create_all)

    yield  # Bắt đầu chạy các hàm Test

    # Teardown: Xóa sạch bảng sau khi chạy xong tất cả các Test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


# ============================================================
# FIXTURE: Database Session với Transaction Rollback
# ============================================================
@pytest_asyncio.fixture()
async def db_session(_mock_redis_cache):
    """
    CƠ CHẾ TRANSACTION ROLLBACK.
    Phụ thuộc vào _mock_redis_cache để tự động mock Redis.
    """
    engine = create_async_engine(settings.DATABASE_URL, echo=False, poolclass=NullPool)
    async with engine.connect() as conn:
        transaction = await conn.begin()

        async_session = AsyncSession(
            bind=conn, expire_on_commit=False, join_transaction_mode="create_savepoint"
        )

        yield async_session

        # Teardown: Rút lại toàn bộ dữ liệu vừa cấy vào DB
        await async_session.close()
        await transaction.rollback()
    await engine.dispose()


# ============================================================
# FIXTURE: HTTP Client giả lập
# ============================================================
@pytest_asyncio.fixture()
async def client(db_session: AsyncSession):
    """
    Giả lập HTTP Client.
    Kế thừa _mock_redis_cache thông qua db_session.
    """
    app.dependency_overrides[get_db] = lambda: db_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
