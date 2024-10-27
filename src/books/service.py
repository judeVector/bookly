from datetime import datetime

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from sqlalchemy.exc import NoResultFound

from .models import Book
from .schemas import BookCreateModel, BookUpdateModel


class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_book(self, book_uid: str, session: AsyncSession):
        try:
            statement = select(Book).where(Book.uid == book_uid)
            result = await session.exec(statement)
            book = result.one()
            return book
        except NoResultFound:
            return None

    async def create_book(
        self, book_data: BookCreateModel, user_uid: str, session: AsyncSession
    ):
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict)
        new_book.published_date = datetime.strptime(
            book_data_dict["published_date"], "%Y-%m-%d"
        )
        new_book.user_id = user_uid

        session.add(new_book)
        await session.commit()
        await session.refresh(new_book)
        return new_book

    async def update_book(
        self, book_uid: str, update_data: BookUpdateModel, session: AsyncSession
    ):
        book_to_update = await self.get_book(book_uid, session)
        if book_to_update:
            update_data_dict = update_data.model_dump()

            for k, v in update_data_dict.items():
                setattr(book_to_update, k, v)

            await session.commit()
            await session.refresh(book_to_update)
            return book_to_update
        return None

    async def delete_book(self, book_uid: str, session: AsyncSession):

        book_to_delete = await self.get_book(book_uid, session)
        if book_to_delete:
            await session.delete(book_to_delete)
            await session.commit()
            return True
        return None

    async def get_user_books(self, user_uid: str, session: AsyncSession):
        try:
            statement = (
                select(Book)
                .where(Book.user_id == user_uid)
                .order_by(desc(Book.created_at))
            )
            result = await session.exec(statement)
            book = result.all()
            return book
        except NoResultFound:
            return None
