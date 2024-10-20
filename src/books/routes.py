from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession

from .service import BookService
from src.db.main import get_session
from .schemas import BookCreateModel, BookModel, BookUpdateModel

book_router = APIRouter()
book_service = BookService()


@book_router.get("/", response_model=List[BookModel])
async def get_all_books(session: AsyncSession = Depends(get_session)):
    books = await book_service.get_all_books(session)
    return books


@book_router.get("/{book_uid}", response_model=BookModel)
async def get_book(book_uid: UUID, session: AsyncSession = Depends(get_session)):
    book = await book_service.get_book(book_uid, session)

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with uid: {book_uid} not found",
        )

    return book


@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=BookModel)
async def create_a_book(
    book_data: BookCreateModel, session: AsyncSession = Depends(get_session)
):

    new_book = await book_service.create_book(book_data, session)
    return new_book


@book_router.patch("/{book_uid}", response_model=BookUpdateModel)
async def update_book(
    book_uid: UUID,
    book_update_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
):
    updated_book = await book_service.update_book(book_uid, book_update_data, session)

    if not updated_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with uid: {book_uid} not found",
        )

    return updated_book


@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_uid: UUID, session: AsyncSession = Depends(get_session)):
    deleted = await book_service.delete_book(book_uid, session)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with uid: {book_uid} not found",
        )

    return None
