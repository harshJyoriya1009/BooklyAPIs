from pydantic import BaseModel, Field
from app.books.schemas import Book
from datetime import datetime
from typing import List, Optional
import uuid

class UserCreateModel(BaseModel):
    username: str = Field(max_length=20, min_length=5)
    email:str= Field(min_length=5)
    password:str = Field(min_length=5)


class UserLoginModel(BaseModel):
    email:str= Field(max_length=40)
    password:str = Field(min_length=5)

class UserModel(BaseModel):
    uid:uuid.UUID
    username:str 
    email:str
    is_verified:bool 
    password_hash:str = Field(exclude=True)
    created_at:datetime 
    updated_at:datetime 
    books: Optional[List[Book]] = []


class EmailModel(BaseModel):
    addresses:List[str]

class PasswordResetRequestModel(BaseModel):
    email:str

class PasswordResetConfirmModel(BaseModel):
    new_password:str
    confirm_new_password:str
