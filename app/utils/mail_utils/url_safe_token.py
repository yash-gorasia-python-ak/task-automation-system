from fastapi import status
from itsdangerous import URLSafeTimedSerializer
from app.core.config import settings
from fastapi import HTTPException


serializer = URLSafeTimedSerializer(
    secret_key=settings.ACCESS_SECRET_KEY, salt="email-configuration"
)


def create_url_safe_token(email: dict) -> str:

    token = serializer.dumps(email)

    return token


def decode_url_safe_token(token: str) -> dict:
    try:
        token_data = serializer.loads(token, max_age=600)

        return token_data

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}",
        )
