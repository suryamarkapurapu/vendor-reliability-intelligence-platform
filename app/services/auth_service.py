"""
Service layer for Authentication business logic operations.
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.auth import create_access_token
from app.core.exceptions import InvalidUserDataError
from app.core.security import get_password_hash, verify_password
from app.models.users import User
from app.repositories.password_reset_repository import password_reset_repository
from app.repositories.user_repository import (
    UserRepository,
    user_repository,
)
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import user_service
from app.utils.email_service import email_service


class AuthService:
    """
    Service layer responsible for user authentication, password resets, and JWT token creation.
    """

    def __init__(self, repo: UserRepository | None = None) -> None:
        self.repo = repo or user_repository

    async def authenticate_user(
        self,
        db: AsyncSession,
        username: str,
        password: str,
    ) -> User:
        """
        Authenticates a user using username/email and password.

        Raises:
            InvalidUserDataError: If the user account is inactive or password is invalid.
        """
        # First attempt lookup by username
        user = await self.repo.get_user_by_username(db, username)

        # If not found by username, attempt lookup by email
        if not user:
            user = await self.repo.get_user_by_email(db, username)

        if not user:
            raise InvalidUserDataError("Invalid username or password.")

        if not user.is_active:
            raise InvalidUserDataError("User account is inactive.")

        if not verify_password(password, user.password_hash):
            raise InvalidUserDataError("Invalid username or password.")

        return user

    async def login(
        self,
        db: AsyncSession,
        login_data: LoginRequest,
    ) -> TokenResponse:
        """
        Authenticates user credentials and generates a signed JWT access token.

        Raises:
            InvalidUserDataError: If authentication fails or account is inactive.
        """
        user = await self.authenticate_user(
            db=db,
            username=login_data.username,
            password=login_data.password,
        )

        payload = {
            "sub": str(user.user_id),
            "email": user.email,
            "role": user.role.role_name,
        }

        access_token = create_access_token(data=payload)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
        )

    async def register_user(
        self,
        db: AsyncSession,
        register_data: RegisterRequest,
    ) -> UserResponse:
        """
        Registers a new user account by reusing user_service.create_user.
        """
        uname = register_data.username
        if not uname or len(uname.strip()) < 3:
            raw_prefix = str(register_data.email).split("@")[0]
            clean_prefix = "".join(c for c in raw_prefix if c.isalnum() or c in ("_", "-"))
            uname = clean_prefix if len(clean_prefix) >= 3 else f"{clean_prefix}user"
            uname = uname[:50]

        user_create = UserCreate(
            username=uname,
            full_name=register_data.full_name,
            email=register_data.email,
            password=register_data.password,
            role_id=register_data.role_id,
        )
        return await user_service.create_user(db, user_create)

    async def request_password_reset(
        self,
        db: AsyncSession,
        forgot_data: ForgotPasswordRequest,
    ) -> dict[str, str]:
        """
        Processes password reset requests:
        1. Checks if user exists.
        2. Generates secure random reset token and computes SHA-256 hash.
        3. Persists hashed token to password_reset_tokens table.
        4. Sends reset email via EmailService asynchronously.
        """
        email_str = str(forgot_data.email).strip().lower()
        user = await self.repo.get_user_by_email(db, email_str)

        if user:
            raw_token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
            expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.RESET_TOKEN_EXPIRE_HOURS)

            await password_reset_repository.create_token(
                db=db,
                user_id=user.user_id,
                token_hash=token_hash,
                expires_at=expires_at,
            )

            await email_service.send_password_reset_email(
                email_to=user.email,
                token=raw_token,
            )

        return {
            "message": "If the email address is registered, password reset instructions have been sent."
        }

    async def reset_password(
        self,
        db: AsyncSession,
        reset_data: ResetPasswordRequest,
    ) -> dict[str, str]:
        """
        Executes password reset:
        1. Hashes incoming token to compare with DB.
        2. Validates token existence, expiration, and unused status.
        3. Hashes new password and updates user password_hash.
        4. Immediately invalidates reset token (one-time use).
        """
        token_hash = hashlib.sha256(reset_data.token.encode()).hexdigest()
        token_record = await password_reset_repository.get_valid_token(db, token_hash)

        if not token_record:
            raise InvalidUserDataError("Invalid or expired password reset token.")

        user = await self.repo.get_user_by_id(db, token_record.user_id)
        if not user:
            raise InvalidUserDataError("User not found for reset token.")

        new_password_hash = get_password_hash(reset_data.new_password)
        await self.repo.update_user(db, user, {"password_hash": new_password_hash})

        await password_reset_repository.invalidate_token(db, token_record)

        return {
            "message": "Password has been successfully reset. You may now log in with your new password."
        }


auth_service = AuthService()
