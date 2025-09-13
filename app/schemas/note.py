from datetime import datetime

from pydantic import BaseModel


class NoteCreate(BaseModel):
    content: str


class NoteOut(BaseModel):
    id: int
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
