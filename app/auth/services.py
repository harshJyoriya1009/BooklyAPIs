from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.database.models import User
from .schemas import UserCreateModel
from .utils import generate_hash_pasword, verify_hash_password

class UserServices:

    async def get_user_by_email(self, email:str, session:AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.execute(statement)
        user = result.scalar_one_or_none()
        return user
    

    async def user_exists(self, email:str, session:AsyncSession):
        user = await self.get_user_by_email(email,session)
        if user is None:
            return False
        else:
            return True


    async def create_user(self, user_data:UserCreateModel, session:AsyncSession):
        user_data_dict = user_data.model_dump()
        password = user_data_dict.pop("password")
        new_user = User(**user_data_dict)

        new_user.password_hash = generate_hash_pasword(password)
        new_user.role = "user"
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    
    
    async def update_user(self, user:User, user_data:dict, session:AsyncSession):
        for key, value in user_data.items():
            setattr(user, key, value)

        await session.commit()
        return user

