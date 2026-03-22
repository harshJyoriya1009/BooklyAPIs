from fastapi.security import HTTPBearer
from fastapi import Request, Depends
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession
from .utils import decode_access_token
from app.database.redis import token_in_blocklist
from app.database.main import get_session
from .services import UserServices
from typing import List, Any
from app.database.models import User
from app.errors import (InvalidTokenException, 
                        RevokedTokenException, 
                        AccessTokenRequiredException, 
                        RefreshTokenRequiredException, 
                        InsufficentPermissionException,
                        AccountNotVerifiedException)


user_service = UserServices()

class TokenBearer(HTTPBearer):
    
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        token = creds.credentials
        token_data = decode_access_token(token)

        if not self.token_valid(token):
            raise InvalidTokenException()
        

        if await token_in_blocklist(token_data['jti']):
            raise RevokedTokenException()

        self.verify_token_data(token_data)
        return token_data
    
    def token_valid(self, token:str)->bool:
        token_data = decode_access_token(token)

        if token_data is not None:
            return True
        else: 
            return False
        
    def verify_token_data(self, token_data):
        raise NotImplementedError("Please override this method in child classes")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data:dict)->None:
         if token_data and token_data['refresh']:
             raise AccessTokenRequiredException()
        

class RefreshTokenBearer(TokenBearer):
       def verify_token_data(self, token_data:dict)->None:
         if token_data and not token_data['refresh']:
             raise RefreshTokenRequiredException()
        
async def get_current_user(token_data:dict = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)):
    user_email = token_data['user']['email']
    user = await user_service.get_user_by_email(user_email, session)
    return user



class RoleChecker:
    def __init__(self, allowed_roles:List[str])-> None:
        self.allowed_roles = allowed_roles
    
    def __call__(self,current_user:User = Depends(get_current_user))->Any:
        if not current_user.is_verified:
            raise AccountNotVerifiedException()
        if current_user.role in self.allowed_roles:
            return True
        raise InsufficentPermissionException()