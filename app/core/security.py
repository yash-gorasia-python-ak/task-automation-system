import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hash: str):
    return pwd_context.verify(password, hash)


def create_access_token(data: dict):

    exp = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "user": data,
        "exp": int(exp.timestamp()),
    }

    token = jwt.encode(
        payload=payload, key=settings.ACCESS_SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return token


def create_refresh_token(data: dict):

    exp = datetime.now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "user": data,
        "exp": int(exp.timestamp()),
    }

    token = jwt.encode(
        payload=payload, key=settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return token


def decode_token(token: str):
    try:
        token_data = jwt.decode(
            jwt=token, key=settings.ACCESS_SECRET_KEY, algorithms=settings.ALGORITHM
        )

        return token_data

    except jwt.PyJWTError as e:
        raise e
