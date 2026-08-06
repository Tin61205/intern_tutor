import logging

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache
from app.core.enums import UserRole
from app.core.exceptions import (
    EmailAlreadyExistsException,
    UserNotFoundException,
    WrongCredentialsException,
)
from app.core.security import PasswordHasher, create_access_token
from app.repositories.user import user_repository
from app.schemas.user import (
    TokenResponse,
    UserCreate,
    UserRegister,
    UserResponse,
    UserUpdate,
)

logger = logging.getLogger("business")


class UserService:
    @classmethod
    async def get_all(cls, db: AsyncSession, skip: int = 0, limit: int = 10):
        # Service không tự query, mà nhờ Repository làm việc đó
        return await user_repository.get_all(db, skip=skip, limit=limit)

    @classmethod
    async def get_by_id(cls, db: AsyncSession, user_id: int):
        cache_key = f"user:{user_id}"

        # 1. Thử lấy từ Redis
        cached_user = await cache.get(cache_key)
        if cached_user:
            return cached_user

        # 2. Nếu Cache Miss, xuống Database
        user = await user_repository.get_by_id(db, id=user_id)
        if not user:
            raise UserNotFoundException()

        # 3. Lưu vào Cache (Lọc bớt các cột nhạy cảm trước khi lưu)
        user_response = UserResponse.model_validate(user)
        await cache.set(cache_key, user_response)

        return user

    @classmethod
    def _prepare_user_data(cls, password: str, extra_fields: dict) -> dict:
        """
        Helper nội bộ: hash mật khẩu và gán các giá trị mặc định cho User mới.
        """
        return {
            **extra_fields,
            "hashed_password": PasswordHasher.hash_password(password),
            "role": UserRole.USER,
            "is_active": True,
        }

    @classmethod
    async def register(cls, db: AsyncSession, user_in: UserRegister):
        """
        Xử lý logic đăng ký tài khoản cho User.
        """
        # 1. Kiểm tra xem Email đã tồn tại trong hệ thống chưa
        existing_user = await user_repository.get_by_email(db, email=user_in.email)
        if existing_user:
            logger.warning(f"Đăng ký thất bại: Email đã tồn tại ({user_in.email})")
            raise EmailAlreadyExistsException()

        # 2. Xử lý dữ liệu
        raw_data = user_in.model_dump(exclude={"password", "confirm_password"})
        user_data = cls._prepare_user_data(user_in.password, raw_data)

        # 3. Giao nhiệm vụ cho Repository để ghi vào Database
        created_user = await user_repository.create(db, obj_in=user_data)
        logger.info(
            f"User đăng ký thành công: {created_user.email} (ID: {created_user.id})"
        )
        return created_user

    @classmethod
    async def login(
        cls, db: AsyncSession, login_data: OAuth2PasswordRequestForm
    ) -> TokenResponse:
        """
        Xử lý logic đăng nhập:
        Tìm user -> Xác thực password -> Tạo JWT token.
        """
        # 1. Tìm user bằng username (ở đây username chính là email)
        user = await user_repository.get_by_email(db, email=login_data.username)
        if not user:
            logger.warning(f"Đăng nhập thất bại: Sai email ({login_data.username})")
            raise WrongCredentialsException()

        # 2. Xác thực mật khẩu
        if not PasswordHasher.verify_password(
            login_data.password, user.hashed_password
        ):
            logger.warning(f"Đăng nhập thất bại: Sai mật khẩu (User ID: {user.id})")
            raise WrongCredentialsException()

        # 3. Tạo JWT Token
        access_token = create_access_token(data={"sub": str(user.id)})

        logger.info(f"User đăng nhập thành công: ID {user.id}")

        # 4. Trả về Response
        return TokenResponse(access_token=access_token, token_type="bearer")

    @classmethod
    async def create(cls, db: AsyncSession, user_in: UserCreate):
        # 1. Nghiệp vụ: Kiểm tra email trùng
        existing_user = await user_repository.get_by_email(db, email=user_in.email)
        if existing_user:
            raise EmailAlreadyExistsException()

        # 2. Xử lý dữ liệu
        raw_data = user_in.model_dump(exclude={"password"})
        user_data = cls._prepare_user_data(user_in.password, raw_data)

        # 3. Nhờ Repository lưu vào DB
        return await user_repository.create(db, obj_in=user_data)

    @classmethod
    async def update(cls, db: AsyncSession, user_id: int, user_in: UserUpdate):
        # 1. Tìm user
        user = await user_repository.get_by_id(db, id=user_id)
        if not user:
            raise UserNotFoundException()

        # 2. Cập nhật data
        update_data = user_in.model_dump(exclude_unset=True)
        updated_user = await user_repository.update(db, db_obj=user, obj_in=update_data)

        # 3. Xóa Cache cũ để tránh stale data
        await cache.delete(f"user:{user_id}")
        logger.info(f"Đã cập nhật hồ sơ User ID: {user_id}")

        return updated_user

    @classmethod
    async def delete(cls, db: AsyncSession, user_id: int):
        success = await user_repository.delete(db, id=user_id)
        if not success:
            raise UserNotFoundException()

        # Xóa Cache
        await cache.delete(f"user:{user_id}")
        logger.info(f"Đã xóa User ID: {user_id} khỏi hệ thống")

        return True
