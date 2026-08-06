"""
Test tích hợp (Integration Tests) cho Cache (Redis thật).
Cần Redis đang chạy để pass.
Chạy riêng bằng: uv run pytest -m integration tests/test_cache.py
"""

import pytest

from app.core.cache import cache


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cache_set_and_get():
    """Test lưu và lấy dữ liệu từ Redis Cache."""
    key = "test_key:1"
    value = {"name": "TaskHub", "version": "1.0"}

    # Test lưu dữ liệu
    success = await cache.set(key, value, ttl=60)
    assert success is True

    # Test lấy dữ liệu
    cached_data = await cache.get(key)
    assert cached_data is not None
    assert cached_data["name"] == "TaskHub"

    # Test xóa dữ liệu
    deleted = await cache.delete(key)
    assert deleted > 0

    # Kiểm tra lại xem đã bay màu chưa
    cached_data_after_delete = await cache.get(key)
    assert cached_data_after_delete is None
