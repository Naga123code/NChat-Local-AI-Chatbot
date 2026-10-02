
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )

    username: str = Field(
        index=True,
        unique=True,
    )

    hashed_password: str


class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )

    username: str = Field(
        index=True,
    )

    role: str

    content: str

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
