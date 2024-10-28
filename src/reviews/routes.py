from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from .schemas import ReviewCreateModel
from .service import ReviewService

from src.auth.dependencies import get_current_user
from src.db.models import User
from src.db.postgres import get_session

review_router = APIRouter()

review_service = ReviewService()


@review_router.post("/book/{book_uid}")
async def add_review_to_book(
    book_uid: UUID,
    review_data: ReviewCreateModel,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    new_review = await review_service.add_review_to_book(
        email=current_user.email,
        book_uid=book_uid,
        review_data=review_data,
        session=session,
    )

    return new_review
