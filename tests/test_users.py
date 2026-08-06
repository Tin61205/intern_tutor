"""
Test tích hợp (Integration Tests) cho Auth và User API cơ bản.
Dùng HTTP Client giả lập kết hợp Test Database.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test API Đăng ký người dùng mới."""
    payload = {
        "email": "test_integration@taskhub.com",
        "full_name": "Test User",
        "password": "password123",
        "confirm_password": "password123",
    }

    response = await client.post("/api/v1/auth/register", json=payload)

    # Kiểm tra mã trạng thái trả về
    assert response.status_code == 201

    # Kiểm tra cấu trúc dữ liệu JSON
    data = response.json()
    assert data["data"]["email"] == "test_integration@taskhub.com"
    # Đảm bảo không bao giờ trả về password
    assert "password" not in data["data"]
    assert "hashed_password" not in data["data"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    """Test API Đăng nhập và lấy Token."""
    # 1. Đăng ký trước một user ảo để có data test đăng nhập
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "login_test@taskhub.com",
            "full_name": "Login User",
            "password": "strongpassword",
            "confirm_password": "strongpassword",
        },
    )

    # 2. Bắn API Đăng nhập (Dùng data form theo chuẩn OAuth2)
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "login_test@taskhub.com",
            "password": "strongpassword",
        },
    )

    assert response.status_code == 200
    data = response.json()
    # Login API trả về chuẩn OAuth2, không bọc trong BaseResponse
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient):
    """Test API Lấy thông tin cá nhân (Cần có JWT Token)."""
    # 1. Khởi tạo dữ liệu
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "me_test@taskhub.com",
            "full_name": "Me User",
            "password": "strongpassword",
            "confirm_password": "strongpassword",
        },
    )

    # 2. Đăng nhập để lấy Token
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "me_test@taskhub.com",
            "password": "strongpassword",
        },
    )
    token = login_response.json()["access_token"]

    # 3. Lấy thông tin cá nhân kèm Header Authorization
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/v1/users/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["email"] == "me_test@taskhub.com"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client: AsyncClient):
    """Test bảo mật: Không có Token thì phải bị cấm truy cập."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401
