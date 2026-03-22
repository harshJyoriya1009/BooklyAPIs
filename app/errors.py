from typing import Any, Callable
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI, status

class BooklyException(Exception):
    # This is base class for all bookly error
    pass


class InvalidTokenException(BooklyException):
    """ User has provided a invalid or expired token"""
    pass


class RevokedTokenException(BooklyException):
    """ User has provided token that has been revoked"""
    pass


class AccessTokenRequiredException(BooklyException):
    """ User has provided a refresh token when a access token needed"""
    pass


class RefreshTokenRequiredException(BooklyException):
    """ User has provided a access token when a refresh token needed"""
    pass


class UserAlreadyExistsException(BooklyException):
    """ User has provided a provided an email for a user who already exists"""
    pass

class InvalidCredentialException(BooklyException):
    """ User has provided a invalid email or password"""
    pass

class InsufficentPermissionException(BooklyException):
    """User does not have permission to perform an action"""
    pass

class BookNotFoundException(BooklyException):
    """Book not found"""
    pass

class UserNotFoundException(BooklyException):
    """User not found"""
    pass

class AccountNotVerifiedException(BooklyException):
    "USer account has not verified yet please, Verify your email"
    pass

def create_exception_handler(status_code: int, initial_detail:Any)->Callable[[Request, Exception], JSONResponse]:
    
    async def exception_handler(request: Request, exec: BooklyException):
        return JSONResponse(
            content=initial_detail,
            status_code=status_code
        )
    
    return exception_handler

def register_all_errors(app: FastAPI):
        app.add_exception_handler(
        UserAlreadyExistsException,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN, 
            initial_detail={
                "message":"User with this email already exists",
                "error_code": "user_exists"
            },
        ),
    )

        app.add_exception_handler(
                UserNotFoundException,
                create_exception_handler(
                    status_code=status.HTTP_404_NOT_FOUND,
                    initial_detail={
                        "message": "User not found",
                        "error_code": "user_not_found",
                    },
                ),
            )

        app.add_exception_handler(
                BookNotFoundException,
                create_exception_handler(
                    status_code=status.HTTP_404_NOT_FOUND,
                    initial_detail={
                        "message": "Book not found",
                        "error_code": "book_not_found",
                    },
                ),
            )

        app.add_exception_handler(
                InvalidCredentialException,
                create_exception_handler(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    initial_detail={
                        "message": "Invalid Email Or Password",
                        "error_code": "invalid_email_or_password",
                    },
                ),
            )

        app.add_exception_handler(
                InvalidTokenException,
                create_exception_handler(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    initial_detail={
                        "message": "Token is invalid Or expired",
                        "resolution": "Please get new token",
                        "error_code": "invalid_token",
                    },
                ),
            )

        app.add_exception_handler(
                RevokedTokenException,
                create_exception_handler(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    initial_detail={
                        "message": "Token is invalid or has been revoked",
                        "resolution": "Please get new token",
                        "error_code": "token_revoked",
                    },
                ),
            )


        app.add_exception_handler(
                AccessTokenRequiredException,
                create_exception_handler(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    initial_detail={
                        "message": "Please provide a valid access token",
                        "resolution": "Please get an access token",
                        "error_code": "access_token_required",
                    },
                ),
            )
        app.add_exception_handler(
                RefreshTokenRequiredException,
                create_exception_handler(
                    status_code=status.HTTP_403_FORBIDDEN,
                    initial_detail={
                        "message": "Please provide a valid refresh token",
                        "resolution": "Please get an refresh token",
                        "error_code": "refresh_token_required",
                    },
                ),
            )

        app.add_exception_handler(
                InsufficentPermissionException,
                create_exception_handler(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    initial_detail={
                        "message": "You do not have enough permissions to perform this action",
                        "error_code": "insufficient_permissions",
                    },
                ),
            )

        app.add_exception_handler(
                BookNotFoundException,
                create_exception_handler(
                    status_code=status.HTTP_404_NOT_FOUND,
                    initial_detail={
                        "message": "Book Not Found",
                        "error_code": "book_not_found",
                    },
                ),
            )
        
        app.add_exception_handler(
            AccountNotVerifiedException,
            create_exception_handler(
                status_code=status.HTTP_403_FORBIDDEN,
                initial_detail={
                    "message": "User account not verified",
                    "error_code": "account_not_verifed",
                    "resolution": "Please check your email for verfication"
                },
            ),
        )


        @app.exception_handler(500)
        async def internal_server_error(request, exc):
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    'message':'OOps something went wrong',
                    'error_code': "server_error"
                }
            )

        