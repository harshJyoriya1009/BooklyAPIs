from fastapi import status, APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.books.services import BookServices
from typing import List
from app.books.schemas import Book, BookUpdate, BookCreate, BookDetailModel
from app.database.main import get_session
from app.auth.dependencies import AccessTokenBearer, RoleChecker
from app.errors import BookNotFoundException
import uuid


book_router = APIRouter()
book_services = BookServices()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(['admin','user']))


@book_router.get("/", response_model=List[Book], dependencies=[role_checker])
async def get_all_books(session: AsyncSession = Depends(get_session), token_details=Depends(access_token_bearer)):
    books = await book_services.get_all_books(session)
    return books


@book_router.get("/user/{user_uid}", response_model=List[Book], dependencies=[role_checker])
async def get_user_books_submission(user_uid:str, session: AsyncSession = Depends(get_session), token_details=Depends(access_token_bearer)):
    books = await book_services.get_user_books(user_uid, session)
    return books


@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book, dependencies=[role_checker])
async def create_book(book_data: BookCreate, session: AsyncSession = Depends(get_session), token_details:dict = Depends(access_token_bearer))->dict:
    user_id = token_details.get('user')["user_uid"]
    new_book = await book_services.create_book(book_data,user_id, session)
    return new_book


@book_router.get("/{book_uid}", response_model=BookDetailModel, dependencies=[role_checker])
async def get_books(book_uid: uuid.UUID, session: AsyncSession = Depends(get_session),token_details:dict = Depends(access_token_bearer))->dict:
    book = await book_services.get_book(book_uid, session)
    if book:
        return book
    else:
        raise BookNotFoundException()


@book_router.patch("/{book_uid}", response_model=Book, dependencies=[role_checker])
async def update_book(book_uid: uuid.UUID, book_data: BookUpdate, session: AsyncSession = Depends(get_session),user_details=Depends(access_token_bearer)):
    updated_book = await book_services.update_book(book_uid, book_data, session)
    if updated_book:
        return updated_book
    else:
        raise BookNotFoundException()


@book_router.delete("/{book_uid}", response_model=Book, dependencies=[role_checker])
async def delete_book(book_uid: uuid.UUID, session: AsyncSession = Depends(get_session),user_details=Depends(access_token_bearer)):
    deleted_book = await book_services.delete_book(book_uid, session)
    if deleted_book:
        return {"message": "Book deleted successfully"}
    else:
        raise BookNotFoundException()