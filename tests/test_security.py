"""
Test đơn vị (Unit Tests) cho Security utilities.
Không cần Database hay Redis.
"""
import pytest

from app.core.security import PasswordHasher, create_access_token


@pytest.mark.unit
def test_password_hasher():
    """Test chức năng mã hóa và giải mã mật khẩu."""
    password = "supersecretpassword"

    # Mã hóa mật khẩu
    hashed = PasswordHasher.hash_password(password)

    assert hashed != password
    assert len(hashed) > 0

    # Kiểm tra giải mã thành công
    is_valid = PasswordHasher.verify_password(password, hashed)
    assert is_valid is True

    # Kiểm tra giải mã thất bại với mật khẩu sai
    is_invalid = PasswordHasher.verify_password("wrongpassword", hashed)
    assert is_invalid is False


@pytest.mark.unit
def test_create_access_token():
    """Test chức năng tạo JWT Token."""
    data = {"sub": "123"}
    token = create_access_token(data=data)

    # Phải trả về một chuỗi JWT
    assert isinstance(token, str)

    # JWT có 3 phần tách nhau bởi dấu chấm
    parts = token.split(".")
    assert len(parts) == 3
