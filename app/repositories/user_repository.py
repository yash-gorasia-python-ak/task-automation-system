from datetime import datetime, timedelta, timezone

from app.models.user_model import User
from app.models.refresh_token_model import RefreshToken
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user_db(self, data: dict) -> User:
        data.update({"role": "user"})
        new_user = User(**data)
        self.db.add(new_user)
        await self.db.flush()

        return new_user

    async def get_by_email(self, email: str):
        res = await self.db.execute(select(User).where(User.email == email))
        return res.scalar_one_or_none()

    async def get_by_id(self, user_id: int):
        res = await self.db.execute(select(User).where(User.user_id == user_id))
        return res.scalar_one_or_none()

    async def list_users(self):
        res = await self.db.execute(select(User))
        return res.scalars().all()

    async def store_refresh_token(self, user_id, refresh_token):
        db_token = RefreshToken(
            token=refresh_token,
            user_id=user_id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            is_used=False,
        )
        self.db.add(db_token)
        await self.db.flush()

    async def get_refresh_token(self, refresh_token):
        res = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token == refresh_token)
        )
        return res.scalar_one_or_none()

    async def security_check(self, user_id):
        await self.db.execute(delete(RefreshToken).where(RefreshToken.user_id == user_id))
        # await self.db.commit()

    async def delete_refresh_token(self, refresh_token):
        await self.db.execute(
            delete(RefreshToken).where(RefreshToken.token == refresh_token)
        )
        # await self.db.commit()
