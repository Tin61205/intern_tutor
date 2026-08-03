"""
Test đơn vị (Unit Tests) cho Mocking techniques.
Không cần Redis thật - dùng Mock để thay thế.
"""
from unittest.mock import AsyncMock

import pytest

from app.core.cache import CacheManager


@pytest.mark.unit
@pytest.mark.asyncio
async def test_mocking_redis(mocker):
    """
    Test kỹ thuật Mocking.
    Thay vì gọi vào Redis thật (có thể bị chậm hoặc rớt mạng khi chạy trên CI/CD Server),
    chúng ta tạo một 'hàm giả' (mock) luôn trả về kết quả cố định siêu tốc.
    """
    # Thay thế (Patch) hàm 'get' của class CacheManager bằng một AsyncMock
    mock_get = mocker.patch.object(
        CacheManager,
        "get",
        new_callable=AsyncMock,
        return_value={"id": 99, "email": "mocked@taskhub.com"},
    )

    # 1. Gọi hàm (Lúc này nó KHÔNG chạy code thật trong cache.py nữa)
    result = await CacheManager.get("user:99")

    # 2. Kiểm chứng
    # Đảm bảo hệ thống có gọi hàm get với đúng tham số "user:99"
    mock_get.assert_called_once_with("user:99")

    # Đảm bảo dữ liệu nhận được đúng là dữ liệu ảo mình đã cài cắm
    assert result["email"] == "mocked@taskhub.com"
