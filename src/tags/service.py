from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from sqlalchemy.exc import NoResultFound

from .schemas import TagAddModel, TagCreateModel

from src.db.models import Tag
from src.books.service import BookService

book_service = BookService()


class TagService:
    async def get_tags(self, session: AsyncSession):
        statement = select(Tag).order_by(desc(Tag.created_at))
        result = await session.exec(statement)
        return result.all()

    async def add_tags_to_book(
        self, book_uid: str, tag_data: TagAddModel, session: AsyncSession
    ):
        try:
            book = await book_service.get_book(book_uid=book_uid, session=session)

            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Book with Id {book_uid} not found",
                )

            for tag_item in tag_data.tags:
                result = await session.exec(
                    select(Tag).where(Tag.name == tag_item.name)
                )

                tag = result.one_or_none()
                if not tag:
                    tag = Tag(name=tag_item.name)

                book.tags.append(tag)
            session.add(book)
            await session.commit()
            await session.refresh(book)
            return book

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Oops... Something went wrong!",
            )

    async def get_tag_by_uid(self, tag_uid: str, session: AsyncSession):

        statement = select(Tag).where(Tag.uid == tag_uid)

        result = await session.exec(statement)

        return result.first()

    async def update_tag(
        self, tag_uid, tag_update_data: TagCreateModel, session: AsyncSession
    ):

        tag = await self.get_tag_by_uid(tag_uid, session)

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tag with Id {tag_uid} not found",
            )

        update_data_dict = tag_update_data.model_dump()

        for k, v in update_data_dict.items():
            setattr(tag, k, v)

            await session.commit()

            await session.refresh(tag)

        return tag
