from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.error.custom_execption import (
    UserAlreadyExists,
    UserNotFound,
    InvalidCredentials,
    InvalidToken,
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.schemas.token_schema import Token
from app.core.config import settings


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = UserRepository(db)

    async def register(self, payload):
        hashed = hash_password(payload.password)
        payload.password = hashed

        async with self.db.begin():
            email = payload.email
            user = await self.repo.get_by_email(email)
            if user:
                raise UserAlreadyExists()

            new_user = await self.repo.create_user_db(payload.model_dump())

        return {
            "message": "Account Created. Check email to verify your account",
            "email": new_user.email,
        }

    async def login(self, payload, response):
        async with self.db.begin():
            user = await self.repo.get_by_email(payload.username)

            if not user:
                raise UserNotFound()

            if not verify_password(payload.password, user.password):
                raise InvalidCredentials()

            access_token = create_access_token(
                {"user_id": user.user_id, "role": user.role}
            )

            refresh_token = create_refresh_token(
                {"user_id": user.user_id, "role": user.role}
            )

            await self.repo.store_refresh_token(user.user_id, refresh_token)

            refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=int(refresh_token_expires.total_seconds()),
            )

            return Token(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
            )

    async def refresh_token(self, payload):
        async with self.db.begin():
            db_token = await self.repo.get_refresh_token(payload.refresh_token)

            if not db_token:
                raise InvalidToken()

            if db_token.is_used:
                await self.repo.security_check(db_token.user_id)

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="All sessions discontinued. Please login again.",
                )

            if db_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(
                timezone.utc
            ):
                await self.repo.delete_refresh_token(db_token.refresh_token)
                raise InvalidToken()

            db_token.is_used = True
            db_user_id = db_token.user_id
            user = await self.repo.get_by_id(db_user_id)

            if not user:
                raise UserNotFound()

            access_token = create_access_token(
                {"user_id": user.user_id, "role": user.role}
            )

            refresh_token = create_refresh_token(
                {"user_id": user.user_id, "role": user.role}
            )

            await self.repo.store_refresh_token(user.user_id, refresh_token)

            return Token(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
            )

    async def logout(self, response, refresh_token):
        async with self.db.begin():
            await self.repo.delete_refresh_token(refresh_token)

            response.delete_cookie(
                key="refresh_token",
                httponly=True,
                secure=True,
                samesite="lax",
            )

            return {"message": "logged out successfully."}
