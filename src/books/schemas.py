import uuid

from typing import List
from datetime import date, datetime
from pydantic import BaseModel


class BookModel(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookDetailModel(BookModel):
    reviews: List
    tags: List


class BookCreateModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str

    class Config:
        from_attributes = True


class BookUpdateModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str

    class Config:
        from_attributes = True
