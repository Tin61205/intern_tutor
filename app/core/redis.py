# app/core/redis.py
import redis.asyncio as redis

from app.core.config import settings


class RedisClient:
    """
    Quản lý kết nối Redis dưới dạng Singleton và Connection Pool.
    Đảm bảo toàn bộ ứng dụng chỉ sử dụng chung một pool kết nối.
    """
    _client: redis.Redis | None = None

    @classmethod
    def get_client(cls) -> redis.Redis:
        """Lấy Redis client hiện tại. Nếu chưa có thì khởi tạo."""
        if cls._client is None:
            # decode_responses=True giúp tự động chuyển Bytes thành String khi đọc data
            cls._client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
            )
        return cls._client

    @classmethod
    async def close(cls):
        """Đóng toàn bộ kết nối trong Pool một cách an toàn."""
        if cls._client:
            await cls._client.aclose()
            cls._client = None
