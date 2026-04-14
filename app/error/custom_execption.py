from typing import Any, Callable, Awaitable
from fastapi.requests import Request
from fastapi.responses import JSONResponse


# Base class
class TaskAutomationExecption(Exception):
    """This is the base class for whole application errors"""

    ...


# Token Error
class InvalidToken(TaskAutomationExecption):
    """User has provided an invalid or expired token"""

    ...


# User Error
class UserNotFound(TaskAutomationExecption):
    """User not found"""

    ...


class UserNotAuthenticated(TaskAutomationExecption):
    """User is not logged in"""

    ...


class UserAlreadyExists(TaskAutomationExecption):
    """User has provided and email for a user who exists during sign up"""

    ...


class InvalidCredentials(TaskAutomationExecption):
    """User has provided wrong email or password during log in"""

    ...


class UserNotVerified(TaskAutomationExecption):
    """User has not completed verification process"""

    ...


# Task Error
class TaskNotFound(TaskAutomationExecption):
    """Task not found"""

    ...


def create_exception_handler(
    status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], Awaitable[JSONResponse]]:

    async def exception_handler(request: Request, exc: Exception):

        return JSONResponse(content=initial_detail, status_code=status_code)

    return exception_handler


def create_global_handler(status_code: int, initial_detail: dict) -> Callable:
    """Factory to create the global handler exception"""

    async def custom_handler(req: Request, exc: Exception):

        error_type = type(exc).__name__
        error_msg = str(exc) if str(exc) else f"Internal {error_type} occurred"

        return JSONResponse(
            status_code=status_code,
            content={
                "status": "error",
                "message": initial_detail.get("message", "Internal Server Error"),
                "error_code": error_type,
                "technical_details": error_msg,
            },
        )

    return custom_handler
