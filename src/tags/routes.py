from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.books.schemas import BookModel

from .schemas import TagAddModel, TagModel, TagCreateModel
from .service import TagService

from src.db.postgres import get_session

tag_router = APIRouter()
tag_service = TagService()


@tag_router.get("", response_model=List[TagModel])
async def get_all_tags(session: AsyncSession = Depends(get_session)):
    tags = await tag_service.get_all_tags(session)

    if not tags:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Error getting all tags"
        )

    return tags


@tag_router.post("", status_code=status.HTTP_201_CREATED, response_model=TagModel)
async def create_a_tag(
    tag_data: TagCreateModel, session: AsyncSession = Depends(get_session)
):
    new_tag = await tag_service.create_tag(tag_data, session)
    return new_tag


@tag_router.post(
    "/books/{book_uid}/tags",
    status_code=status.HTTP_201_CREATED,
    response_model=BookModel,
)
async def add_tag_to_book(
    book_uid: UUID,
    tag_data: TagAddModel,
    session: AsyncSession = Depends(get_session),
) -> BookModel:
    book_with_tag = await tag_service.add_tags_to_book(book_uid, tag_data, session)

    return book_with_tag
