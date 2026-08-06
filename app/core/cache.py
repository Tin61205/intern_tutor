import json
import logging
from typing import Any

from pydantic import BaseModel
from redis.exceptions import RedisError

from app.core.redis import RedisClient

logger = logging.getLogger("redis_cache")


class CacheManager:
    """
    Tầng trung gian (Utility Layer) hỗ trợ thao tác với Redis.
    Tự động lo việc Serialization (biến Pydantic/Dict thành JSON String) và Deserialization.
    """

    @staticmethod
    async def get(key: str) -> dict | list | None:
        """Lấy dữ liệu từ Cache theo Key và chuyển ngược về Dict/List."""
        try:
            client = RedisClient.get_client()
            data = await client.get(key)
            if data:
                return json.loads(data)
            return None
        except RedisError as e:
            logger.warning(f"Redis GET lỗi ({key}): {e}")
            return None

    @staticmethod
    async def set(key: str, value: Any, ttl: int = 300) -> bool:
        """Lưu dữ liệu vào Cache. Mặc định TTL là 300 giây."""
        try:
            client = RedisClient.get_client()

            value_dict: Any
            if isinstance(value, BaseModel):
                value_dict = value.model_dump(mode="json")
            elif isinstance(value, (dict, list)):
                value_dict = value
            else:
                value_dict = str(value)

            json_data = json.dumps(value_dict)
            return bool(await client.set(key, json_data, ex=ttl))
        except RedisError as e:
            logger.warning(f"Redis SET lỗi ({key}): {e}")
            return False

    @staticmethod
    async def delete(key: str) -> int:
        """Xóa một Key khỏi Cache."""
        try:
            client = RedisClient.get_client()
            return await client.delete(key)
        except RedisError as e:
            logger.warning(f"Redis DELETE lỗi ({key}): {e}")
            return 0

    @staticmethod
    async def exists(key: str) -> bool:
        """Kiểm tra xem Key có tồn tại không."""
        try:
            client = RedisClient.get_client()
            return await client.exists(key) > 0
        except RedisError as e:
            logger.warning(f"Redis EXISTS lỗi ({key}): {e}")
            return False

    @staticmethod
    async def expire(key: str, ttl: int) -> bool:
        """Cập nhật lại thời gian sống cho một Key đang tồn tại."""
        try:
            client = RedisClient.get_client()
            return await client.expire(key, ttl)
        except RedisError as e:
            logger.warning(f"Redis EXPIRE lỗi ({key}): {e}")
            return False


# Tạo sẵn một object để sử dụng chung cho toàn project
cache = CacheManager()
