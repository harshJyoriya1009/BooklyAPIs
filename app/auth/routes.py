from fastapi import status, APIRouter, Depends, HTTPException, BackgroundTasks
from datetime import timedelta, datetime
from sqlmodel.ext.asyncio.session import AsyncSession

from .schemas import (
    UserCreateModel, 
    UserLoginModel, 
    UserModel, 
    EmailModel, 
    PasswordResetRequestModel,
    PasswordResetConfirmModel
)
from .utils import (
    create_access_token, 
    verify_hash_password, 
    create_url_safe_token, 
    decode_url_safe_token,
    generate_hash_pasword
)
from fastapi.responses import JSONResponse
from .dependencies import (
    RefreshTokenBearer, 
    AccessTokenBearer, 
    get_current_user, 
    RoleChecker
)
from app.errors import (
    UserAlreadyExistsException, 
    InvalidTokenException, 
    InvalidCredentialException, 
    UserNotFoundException
)
from .services import UserServices

from app.database.redis import add_jti_blocklist
from app.database.main import get_session
from app.mail import mail, create_messsage
from app.config import Config
from app.celery_tasks import send_email


auth_router = APIRouter()
user_services = UserServices()
role_checker = RoleChecker(['admin', 'user'])

REFRESH_TOKEN_EXPIRY=2


@auth_router.post('/send_email')
async def send_mail(emails: EmailModel):
    emails = emails.addresses

    html = "<h1>Welcome to the Bookly app</h1>"
    subject = "Welcome to our Bookly app"

    send_email.delay(emails, subject, html)
    
    return {"message": "Email send successfully"}


@auth_router.post('/register', status_code=status.HTTP_201_CREATED)
async def create_user_Account(user_data:UserCreateModel, bg_tasks:BackgroundTasks, session:AsyncSession = Depends(get_session)):
    email = user_data.email
    user_exists = await user_services.user_exists(email, session)
    if user_exists:
        raise UserAlreadyExistsException()
    
    new_user = await user_services.create_user(user_data, session)

    token = create_url_safe_token({"email": email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"
    html = f"""
        <h1> Verify your email </h1>
        <p> PLease click this <a href="{link}">Link</a> to verify your email </p>
        """
    subject="Verify your email"
    
    emails=[email]
   
    send_email.delay(emails, subject, html)

    return {
        "message": "Account Created! Check your email to verify your account",
        "user": new_user
    }

@auth_router.get('/verify/{token}')
async def verify_user_account(token:str, session:AsyncSession=Depends(get_session)):
    token_data = decode_url_safe_token(token)
    user_email = token_data.get('email')

    if user_email:
        user = await user_services.get_user_by_email(user_email, session)
        if not user:
            raise UserNotFoundException()
        
        await user_services.update_user(user,{"is_verified":True}, session)
        return JSONResponse(
            content={"message": "Account verified successfully"},
            status_code=status.HTTP_200_OK
        )
    
    return JSONResponse(
        content={"message": "Error occupied during the verfication"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


@auth_router.post('/login', status_code=status.HTTP_200_OK)
async def login_user(login_data:UserLoginModel, session:AsyncSession = Depends(get_session)):
    email = login_data.email
    password = login_data.password
    
    user = await user_services.get_user_by_email(email, session)

    if user is not None:
        password_valid = verify_hash_password(password, user.password_hash)

        if password_valid:
            access_token = create_access_token(
                user_data={
                    'email': user.email,
                    "user_uid": str(user.uid),
                    "role":user.role
                }
            )

            refresh_token=create_access_token(
                user_data={
                    'email': user.email,
                    "user_uid": str(user.uid)
                },
                refresh=True,
                expiry_time=timedelta(days=REFRESH_TOKEN_EXPIRY)
            )
            return JSONResponse(
                content={
                    "message": "Login Successfull",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user":{
                        "email": user.email,
                        "uid": str(user.uid)
                    }
                }
            )
    raise InvalidCredentialException()


@auth_router.get('/token')
async def get_new_access_token(token_details:dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details['exp']

    if datetime.fromtimestamp(expiry_timestamp)>datetime.now():
        new_access_token = create_access_token(
            user_data = token_details['user']
        )
        return JSONResponse(content={
            "access_token": new_access_token
        })
    
    raise InvalidTokenException()

@auth_router.get('/me', response_model=UserModel)
async def get_current_user(user = Depends(get_current_user), _:bool = Depends(role_checker)):
    return user


@auth_router.get('/logout')
async def revoke_token(token_details: dict=Depends(AccessTokenBearer())):
    jti = token_details['jti']
    await add_jti_blocklist(jti)
    return JSONResponse(
        content={
            "message": "Logout successfully"
        },
        status_code=status.HTTP_200_OK
    )


@auth_router.post("/password-reset-request")
async def password_reset_request(email_data: PasswordResetRequestModel):
    email = email_data.email

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"

    html = f"""
    <h1>Reset Your Password</h1>
    <p>Please click this <a href="{link}">link</a> to Reset Your Password</p>
    """
    subject = "Reset Your Password"

    emails = [email]
    send_email.delay(emails, subject, html)
    return JSONResponse(
        content={
            "message": "Please check your email for instructions to reset your password",
        },
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/password-reset-confirm/{token}")
async def reset_account_password(
    token: str,
    passwords: PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_session),
):
    new_password = passwords.new_password
    confirm_password = passwords.confirm_new_password

    if new_password != confirm_password:
        raise HTTPException(
            detail="Passwords do not match", status_code=status.HTTP_400_BAD_REQUEST
        )

    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await user_services.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFoundException()

        passwd_hash = generate_hash_pasword(new_password)
        await user_services.update_user(user, {"password_hash": passwd_hash}, session)

        return JSONResponse(
            content={"message": "Password reset Successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during password reset."},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

