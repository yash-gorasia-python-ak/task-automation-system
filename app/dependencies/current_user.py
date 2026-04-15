import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.get_session import get_db
from app.error.custom_execption import UserNotAuthenticated, UserNotFound
from app.repositories.user_repository import UserRepository
from app.schemas.token_schema import TokenData
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    if token is None:
        raise UserNotAuthenticated()

    try:
        payload = jwt.decode(
            token, settings.ACCESS_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except jwt.PyJWTError:
        raise UserNotAuthenticated()
    
    user = await UserRepository(db).get_by_id(payload["user"]["user_id"])
    print(user)
    if not user:
        raise UserNotFound()

    return TokenData(user_id=user.user_id, role=user.role)
