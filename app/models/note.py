from datetime import datetime
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel
from app.models.user import User


class Note(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(nullable=False)
    summary: Optional[str] = Field(default=None, nullable=True)
    status: str = Field(default="idle")  # idle | queued | processing | done | failed
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="notes")
