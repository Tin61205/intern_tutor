# app/core/cache.py
import json
from typing import Any

from pydantic import BaseModel

from app.core.redis import RedisClient


class CacheManager:
    """
    Tầng trung gian (Utility Layer) hỗ trợ thao tác với Redis.
    Tự động lo việc Serialization (biến Pydantic/Dict thành JSON String) và Deserialization.
    """

    @staticmethod
    async def get(key: str) -> dict | list | None:
        """Lấy dữ liệu từ Cache theo Key và chuyển ngược về Dict/List."""
        client = RedisClient.get_client()
        data = await client.get(key)
        if data:
            return json.loads(data)
        return None

    @staticmethod
    async def set(key: str, value: Any, ttl: int = 300) -> bool:
        """
        Lưu dữ liệu vào Cache. Mặc định TTL (Time to live) là 300 giây (5 phút).
        """
        client = RedisClient.get_client()

        # Tiền xử lý dữ liệu trước khi ném vào Redis
        if isinstance(value, BaseModel):
            # Ép Pydantic model thành dict tương thích với JSON (xử lý luôn datetime)
            value_dict = value.model_dump(mode="json")
        elif isinstance(value, (dict, list)):
            value_dict = value
        else:
            value_dict = str(value)

        json_data = json.dumps(value_dict)
        # ex (expire) là tham số quyết định thời gian sống của key tính bằng giây
        return await client.set(key, json_data, ex=ttl)

    @staticmethod
    async def delete(key: str) -> int:
        """Xóa một Key khỏi Cache."""
        client = RedisClient.get_client()
        return await client.delete(key)

    @staticmethod
    async def exists(key: str) -> bool:
        """Kiểm tra xem Key có tồn tại không."""
        client = RedisClient.get_client()
        # exists() trả về số lượng key tìm thấy (0 hoặc 1)
        return await client.exists(key) > 0

    @staticmethod
    async def expire(key: str, ttl: int) -> bool:
        """Cập nhật lại thời gian sống cho một Key đang tồn tại."""
        client = RedisClient.get_client()
        return await client.expire(key, ttl)


# Tạo sẵn một object để sử dụng chung cho toàn project
cache = CacheManager()
