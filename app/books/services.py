from sqlmodel import select
from app.database.models import Book
from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import BookCreate
from sqlmodel import select,desc


class BookServices:

    async def get_all_books(self, session):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.execute(statement)

        books = result.scalars().all()
        return books
    
    
    async def get_user_books(self,user_uid:str, session):
        statement = select(Book).where(Book.user_uid == user_uid).order_by(desc(Book.created_at))
        result = await session.execute(statement)

        books = result.scalars().all()
        return books


    async def get_book(self, book_uid, session):
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.execute(statement)

        book = result.scalar_one_or_none()
        return book


    async def create_book(self, book_data:BookCreate, user_uid:str, session:AsyncSession):
        print("Incoming data:", book_data)
        print("Dumped data:", book_data.model_dump())
    
        new_book = Book(**book_data.model_dump())
        new_book.user_uid = user_uid

        session.add(new_book)
        await session.commit()
        await session.refresh(new_book)

        return new_book


    async def update_book(self, book_uid, book_data, session):
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.execute(statement)

        book = result.scalar_one_or_none()

        if not book:
            return None

        for key, value in book_data.dict(exclude_unset=True).items():
            setattr(book, key, value)

        await session.commit()
        await session.refresh(book)

        return book


    async def delete_book(self, book_uid, session):
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.execute(statement)

        book = result.scalar_one_or_none()

        if not book:
            return None

        await session.delete(book)
        await session.commit()

        return True