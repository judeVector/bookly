from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.books.schemas import BookModel

from .schemas import TagAddModel, TagModel, TagCreateModel
from .service import TagService

from src.db.postgres import get_session
from src.auth.dependencies import Rolechecker

tags_router = APIRouter()
tag_service = TagService()
role_checker = Depends(Rolechecker(["user"]))


@tags_router.get("", response_model=List[TagModel], dependencies=[role_checker])
async def get_all_tags(session: AsyncSession = Depends(get_session)):
    tags = await tag_service.get_all_tags(session)

    if not tags:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Error getting all tags"
        )

    return tags


@tags_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=TagModel,
    dependencies=[role_checker],
)
async def create_a_tag(
    tag_data: TagCreateModel, session: AsyncSession = Depends(get_session)
):
    new_tag = await tag_service.create_tag(tag_data, session)
    return new_tag


@tags_router.post(
    "/books/{book_uid}/tags",
    status_code=status.HTTP_201_CREATED,
    response_model=BookModel,
    dependencies=[role_checker],
)
async def add_tag_to_book(
    book_uid: UUID,
    tag_data: TagAddModel,
    session: AsyncSession = Depends(get_session),
) -> BookModel:
    book_with_tag = await tag_service.add_tags_to_book(book_uid, tag_data, session)

    return book_with_tag


@tags_router.put("/{tag_uid}", response_model=TagModel, dependencies=[role_checker])
async def update_tag(
    tag_uid: str,
    tag_update_data: TagCreateModel,
    session: AsyncSession = Depends(get_session),
) -> TagModel:
    updated_tag = await tag_service.update_tag(tag_uid, tag_update_data, session)

    return updated_tag


@tags_router.delete(
    "/{tag_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[role_checker],
)
async def delete_tag(
    tag_uid: str, session: AsyncSession = Depends(get_session)
) -> None:
    updated_tag = await tag_service.delete_tag(tag_uid, session)

    return updated_tag
