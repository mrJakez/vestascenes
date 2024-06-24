from __future__ import annotations

from typing import List

from Helper.RawHelper import RawHelper
from Models.UUIDSQLModel import UUIDSQLModel


class SnapshotModel(UUIDSQLModel, table=True):
    __tablename__ = "snapshots"

    title: str
    raw: str

    def get_raw_list(self) -> List:
        return RawHelper.get_raw_object(self.raw)