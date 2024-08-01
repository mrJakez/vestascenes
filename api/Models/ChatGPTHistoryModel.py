from __future__ import annotations

import datetime

from sqlmodel import Field

from Models.UUIDSQLModel import UUIDSQLModel


class ChatGPTHistoryModel(UUIDSQLModel, table=True):
    __tablename__ = "chatgpt_history"

    role: str
    content: str
    author: str = Field(default=None)
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow,
    )
