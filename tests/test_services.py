"""
Test tích hợp (Integration Tests) cho tầng Service.
Test trực tiếp UserService với DB session thật (không qua HTTP).
Redis đã được mock tự động qua fixture db_session trong conftest.py.
"""
import pytest
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserRegister, UserUpdate
from app.services.user_service import UserService


@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_service_register(db_session: AsyncSession):
    """Test đăng ký user qua Service layer."""
    user_in = UserRegister(
        email="service_register@taskhub.com",
        full_name="Service Register",
        password="password123",
        confirm_password="password123",
    )
    user = await UserService.register(db_session, user_in)
    assert user.email == "service_register@taskhub.com"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_service_login(db_session: AsyncSession):
    """Test đăng nhập user qua Service layer."""
    user_in = UserRegister(
        email="service_login@taskhub.com",
        full_name="Service Login",
        password="password123",
        confirm_password="password123",
    )
    await UserService.register(db_session, user_in)

    login_data = OAuth2PasswordRequestForm(
        username="service_login@taskhub.com", password="password123"
    )
    token = await UserService.login(db_session, login_data)
    assert token.access_token is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_service_create(db_session: AsyncSession):
    """Test tạo user bằng Admin API qua Service layer."""
    user_in = UserCreate(
        email="service_create@taskhub.com",
        full_name="Service Create",
        password="password123",
    )
    user = await UserService.create(db_session, user_in)
    assert user.email == "service_create@taskhub.com"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_service_get_by_id(db_session: AsyncSession):
    """Test lấy user theo ID qua Service layer (cache miss → DB)."""
    user_in = UserCreate(
        email="service_get@taskhub.com",
        full_name="Service Get",
        password="password123",
    )
    user = await UserService.create(db_session, user_in)

    fetched = await UserService.get_by_id(db_session, user.id)
    assert fetched.id == user.id


@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_service_update(db_session: AsyncSession):
    """Test cập nhật user qua Service layer."""
    user_in = UserCreate(
        email="service_update2@taskhub.com",
        full_name="Service Update",
        password="password123",
    )
    user = await UserService.create(db_session, user_in)

    update_in = UserUpdate(full_name="Updated Name")
    updated = await UserService.update(db_session, user.id, update_in)
    assert updated.full_name == "Updated Name"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_service_delete(db_session: AsyncSession):
    """Test xóa user qua Service layer."""
    user_in = UserCreate(
        email="service_delete2@taskhub.com",
        full_name="Service Delete",
        password="password123",
    )
    user = await UserService.create(db_session, user_in)

    success = await UserService.delete(db_session, user.id)
    assert success is True
