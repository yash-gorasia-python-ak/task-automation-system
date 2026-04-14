from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.error.custom_execption import (
    InvalidToken,
    UserNotFound,
    UserNotAuthenticated,
    UserAlreadyExists,
    InvalidCredentials,
    UserNotVerified,
    TaskNotFound,
    create_exception_handler,
    create_global_handler,
)


def register_all_error(app: FastAPI):

    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid or expired",
                "resolution": "Please get new token",
                "error_code": "invalid_token",
            },
        ),
    )

    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User not found",
                "error_code": "user_not_found",
            },
        ),
    )

    app.add_exception_handler(
        UserNotAuthenticated,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Please log in to access this resource",
                "error_code": "user_not_authenticated",
            },
        ),
    )

    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "User with email already exists",
                "error_code": "user_exists",
            },
        ),
    )

    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Invalid Email Or Password",
                "error_code": "invalid_email_or_password",
            },
        ),
    )

    app.add_exception_handler(
        UserNotVerified,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "You have not verified the account",
                "resolution": "check your email, and complete verification process",
                "error_code": "user_not_verified",
            },
        ),
    )

    app.add_exception_handler(
        TaskNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Task not found",
                "error_code": "task_not_found",
            },
        ),
    )

    app.add_exception_handler(
        Exception,
        create_global_handler(
            status_code=500,
            initial_detail={
                "message": "Internal Server Error",
            },
        ),
    )
