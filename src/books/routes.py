from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession

from .service import BookService
from .schemas import BookCreateModel, BookModel, BookUpdateModel, BookDetailModel

from src.db.postgres import get_session
from src.auth.dependencies import AccessTokenBearer, Rolechecker


book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(Rolechecker(["user"]))


@book_router.get("", response_model=List[BookModel], dependencies=[role_checker])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    books = await book_service.get_all_books(session)
    return books


@book_router.get(
    "/user/{user_uid}", response_model=List[BookModel], dependencies=[role_checker]
)
async def get_user_book_submissions(
    user_uid: UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):

    books = await book_service.get_user_books(user_uid, session)
    return books


@book_router.get(
    "/{book_uid}", response_model=BookDetailModel, dependencies=[role_checker]
)
async def get_book(
    book_uid: UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    book = await book_service.get_book(book_uid, session)

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with uid: {book_uid} not found",
        )

    return book


@book_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=BookModel,
    dependencies=[role_checker],
)
async def create_a_book(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):

    user_id = token_details.get("user")["user_uid"]
    print(user_id)
    print(token_details)
    new_book = await book_service.create_book(book_data, user_id, session)
    return new_book


@book_router.patch(
    "/{book_uid}", response_model=BookUpdateModel, dependencies=[role_checker]
)
async def update_book(
    book_uid: UUID,
    book_update_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    updated_book = await book_service.update_book(book_uid, book_update_data, session)

    if not updated_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with uid: {book_uid} not found",
        )

    return updated_book


@book_router.delete(
    "/{book_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker]
)
async def delete_book(
    book_uid: UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    deleted = await book_service.delete_book(book_uid, session)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with uid: {book_uid} not found",
        )

    return None
