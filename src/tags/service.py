from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from sqlalchemy.exc import NoResultFound

from .schemas import TagAddModel, TagCreateModel

from src.db.models import Tag
from src.books.service import BookService

book_service = BookService()


class TagService:
    async def get_all_tags(self, session: AsyncSession):
        statement = select(Tag).order_by(desc(Tag.created_at))
        result = await session.exec(statement)
        return result.all()

    # async def create_tag(self, tag_data: TagCreateModel, session: AsyncSession):
    #     tag_data_dict = tag_data.model_dump()
    #     new_tag = Tag(**tag_data_dict)

    #     session.add(new_tag)
    #     await session.commit()
    #     await session.refresh(new_tag)
    #     return new_tag

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
                detail="Oops... Somwthing went wrong!",
            )
