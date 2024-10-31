import uuid
from datetime import datetime

from typing import List
from pydantic import BaseModel, Field


class TagModel(BaseModel):
    uid: uuid.UUID
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class TagCreateModel(BaseModel):
    name: str = Field(max_length=20)


class TagAddModel(BaseModel):
    tags: List[TagCreateModel]
