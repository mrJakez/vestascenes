from __future__ import annotations
from Models.UUIDSQLModel import UUIDSQLModel
from sqlmodel import SQLModel, Field
import datetime


class ChatGPTHistoryModel(UUIDSQLModel, table=True):
    __tablename__ = "chatgpt_history"

    role: str
    content: str
    author: str = Field(default=None)
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow,
    )