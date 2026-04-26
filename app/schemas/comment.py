from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    body: str = Field(..., min_length=1, max_length=5000)


class CommentUpdate(BaseModel):
    body: str = Field(..., min_length=1, max_length=5000)


class CommentOut(BaseModel):
    id: int
    body: str
    task_id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
