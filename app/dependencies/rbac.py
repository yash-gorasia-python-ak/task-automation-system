from typing import Annotated
from fastapi import Depends, HTTPException, status
from app.schemas.token_schema import TokenData
from app.dependencies.current_user import get_current_user

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: Annotated[TokenData , Depends(get_current_user)]):

        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have the required permissions"
            )
        return user
