import uuid
from datetime import datetime

from typing import List
from pydantic import BaseModel, Field

from src.books.schemas import BookModel


class UserCreateModel(BaseModel):
    username: str = Field(max_length=20)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)
    first_name: str = Field(max_length=20)
    last_name: str = Field(max_length=20)

    class Config:
        from_attributes = True


class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool
    password_hash: str = Field(exclude=True)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserBooksModel(UserModel):
    books: List[BookModel]
    reviews: List


class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)

    class Config:
        from_attributes = True
