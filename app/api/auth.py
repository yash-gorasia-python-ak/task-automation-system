from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user_schema import RegisterRequest, RegisterResponse
from app.schemas.token_schema import RefreshToken

from app.dependencies.get_session import get_db
from app.services.auth_service import AuthService

auth_router = APIRouter()


@auth_router.post("/register", response_model=RegisterResponse)
async def register(
    payload: RegisterRequest, db: Annotated[AsyncSession, Depends(get_db)]
):

    return await AuthService(db).register(payload)


@auth_router.post("/login")
async def login(
    response: Response,
    payload: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):

    return await AuthService(db).login(payload, response)


@auth_router.post("/refresh")
async def refresh_token(
    payload: RefreshToken, response: Response, db: Annotated[AsyncSession, Depends(get_db)]
):
    return await AuthService(db).refresh_token(payload, response)


@auth_router.post("/logout")
async def logout(
    db: Annotated[AsyncSession, Depends(get_db)],
    response: Response,
    refresh_token: Optional[str] = Cookie(None, alias="refresh_token"),
):
    return await  AuthService(db).logout(response, refresh_token)
