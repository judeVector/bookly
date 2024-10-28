from msilib.text import tables
import uuid
from datetime import date, datetime

from sqlmodel import Field, SQLModel, Column, Relationship, desc
from typing import Optional, List
import sqlalchemy.dialects.postgresql as pg


# User Model
class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    username: str
    email: str
    first_name: str
    last_name: str
    role: str = Field(
        sa_column=Column(pg.VARCHAR, nullable=False, server_default="user")
    )
    password_hash: str = Field(exclude=True)
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    books: List["Book"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin", "order_by": desc("created_at")},
    )
    reviews: List["Review"] = Relationship(
        back_populates="user",  # Corrected back_populates to match Review model
        sa_relationship_kwargs={"lazy": "selectin", "order_by": desc("created_at")},
    )

    def __repr__(self):
        return f"<User {self.username}>"


# Book Model
class Book(SQLModel, table=True):
    __tablename__ = "books"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    user: Optional["User"] = Relationship(back_populates="books")
    reviews: List["Review"] = Relationship(
        back_populates="book",  # Corrected back_populates to match Review model
        sa_relationship_kwargs={"lazy": "selectin", "order_by": desc("created_at")},
    )

    def __repr__(self):
        return f"<Book {self.title}>"


# Review Model
class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    rating: int = Field(lt=5)
    review_text: str
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    book_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="books.uid")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    user: Optional["User"] = Relationship(back_populates="reviews")  # Linked to User
    book: Optional["Book"] = Relationship(back_populates="reviews")  # Linked to Book

    def __repr__(self):
        return f"<Review for book {self.book_uid} by user {self.user_uid}>"
