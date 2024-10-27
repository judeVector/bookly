import uuid
from datetime import datetime

from sqlalchemy import Column, desc
from typing import List
from sqlmodel import Field, Relationship, SQLModel
import sqlalchemy.dialects.postgresql as pg

from src.books import models


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
    books: List["models.Book"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin", "order_by": desc("created_at")},
    )

    def __repr__(self):
        return f"<User {self.username}>"
