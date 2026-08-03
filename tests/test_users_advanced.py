"""
Test tích hợp (Integration Tests) nâng cao cho User API.
Kiểm tra phân quyền ADMIN/USER, CRUD đầy đủ và các trường hợp lỗi.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import UserRole
from app.core.security import PasswordHasher
from app.models.users import User


async def create_test_user(
    db_session: AsyncSession, email: str, role: UserRole = UserRole.USER
):
    user = User(
        email=email,
        full_name="Test User",
        hashed_password=PasswordHasher.hash_password("password123"),
        role=role,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_all_users_as_admin(client: AsyncClient, db_session: AsyncSession):
    """Test lấy danh sách người dùng với quyền ADMIN."""
    admin = await create_test_user(db_session, "admin1@taskhub.com", UserRole.ADMIN)

    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": admin.email, "password": "password123"},
    )
    token = login_res.json()["access_token"]

    res = await client.get(
        "/api/v1/users/", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_all_users_as_normal_user(
    client: AsyncClient, db_session: AsyncSession
):
    """Test lấy danh sách người dùng với quyền USER (sẽ bị cấm - 403)."""
    user = await create_test_user(db_session, "user1@taskhub.com", UserRole.USER)

    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": "password123"},
    )
    token = login_res.json()["access_token"]

    res = await client.get(
        "/api/v1/users/", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 403


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_user(client: AsyncClient, db_session: AsyncSession):
    """Test chức năng cập nhật thông tin User."""
    user = await create_test_user(db_session, "update@taskhub.com", UserRole.USER)

    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": "password123"},
    )
    token = login_res.json()["access_token"]

    payload = {"full_name": "Updated Name"}
    res = await client.patch(
        f"/api/v1/users/{user.id}",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 200
    assert res.json()["data"]["full_name"] == "Updated Name"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient, db_session: AsyncSession):
    """Test chức năng xóa User."""
    user = await create_test_user(db_session, "delete@taskhub.com", UserRole.USER)

    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": "password123"},
    )
    token = login_res.json()["access_token"]

    res = await client.delete(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200

    # Kiểm tra lại: token của user bị xóa sẽ không lấy được data nữa
    res_check = await client.get(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_check.status_code in [404, 401]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test Exception khi đăng ký trùng Email."""
    payload = {
        "email": "duplicate@taskhub.com",
        "full_name": "Test User",
        "password": "password123",
        "confirm_password": "password123",
    }

    # Đăng ký lần 1
    res1 = await client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    # Đăng ký lần 2 trùng email
    res2 = await client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 400
    assert res2.json()["error_code"] == "BAD_REQUEST"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, db_session: AsyncSession):
    """Test Exception khi đăng nhập sai mật khẩu."""
    user = await create_test_user(db_session, "wrongpass@taskhub.com", UserRole.USER)

    res = await client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": "wrong"},
    )
    assert res.status_code == 401
    assert res.json()["error_code"] == "UNAUTHORIZED"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_non_existent_user(client: AsyncClient, db_session: AsyncSession):
    """Test lấy user không tồn tại (404)."""
    admin = await create_test_user(
        db_session, "admin_notfound@taskhub.com", UserRole.ADMIN
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": admin.email, "password": "password123"},
    )
    token = login_res.json()["access_token"]

    res = await client.get(
        "/api/v1/users/999999", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 404
    assert res.json()["error_code"] == "NOT_FOUND"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_non_existent_user(client: AsyncClient, db_session: AsyncSession):
    """Test cập nhật user không tồn tại (404)."""
    admin = await create_test_user(
        db_session, "admin_update_notfound@taskhub.com", UserRole.ADMIN
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": admin.email, "password": "password123"},
    )
    token = login_res.json()["access_token"]

    res = await client.patch(
        "/api/v1/users/999999",
        json={"full_name": "New Name"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 404


@pytest.mark.integration
@pytest.mark.asyncio
async def test_delete_non_existent_user(client: AsyncClient, db_session: AsyncSession):
    """Test xóa user không tồn tại (404)."""
    admin = await create_test_user(
        db_session, "admin_delete_notfound@taskhub.com", UserRole.ADMIN
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": admin.email, "password": "password123"},
    )
    token = login_res.json()["access_token"]

    res = await client.delete(
        "/api/v1/users/999999", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 404
