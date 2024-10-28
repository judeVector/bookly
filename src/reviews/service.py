from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio.session import AsyncSession

from .schemas import ReviewCreateModel

from src.db.models import Review
from src.auth.service import UserService
from src.books.service import BookService


user_service = UserService()
book_service = BookService()


class ReviewService:

    async def add_review_to_book(
        self,
        email: str,
        book_uid: str,
        review_data: ReviewCreateModel,
        session: AsyncSession,
    ):
        try:
            book = await book_service.get_book(book_uid, session)
            user = await user_service.get_user_by_email(email, session)
            new_review = Review(**review_data.model_dump())

            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Book with Id {book_uid} not found",
                )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with email {email} not found",
                )

            new_review.user = user
            new_review.book = book

            session.add(new_review)
            await session.commit()
            await session.refresh(new_review)
            return new_review

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Oops... Somwthing went wrong!",
            )
