from __future__ import annotations

from datetime import datetime
from typing import List, Any

from sqlmodel import Field, SQLModel

from Helper.RawHelper import RawHelper
# from api.Scenes import AbstractScene
from Scenes import AbstractScene


class SceneInstanceModel(SQLModel, table=True):
    __tablename__ = "scene_instances"

    id: str = Field(default=None, primary_key=True)
    class_string: str
    start_date: str
    end_date: str
    raw: str
    priority: int
    is_active: bool

    def __init__(self, scene: AbstractScene, **data: Any):
        super().__init__(**data)
        self.id = scene.id
        self.class_string = scene.scene_object.__class__.__name__
        self.raw = RawHelper.get_raw_string(scene.raw)
        self.start_date = scene.start_date
        self.end_date = scene.end_date
        self.priority = scene.priority
        self.is_active = True

    def get_raw_list(self) -> List:
        return RawHelper.get_raw_object(self.raw)

    def get_end_date(self) -> datetime:
        try:
            real_date = datetime.strptime(self.end_date, "%Y-%m-%d %H:%M:%S.%f")
            return real_date
        except ValueError as e:
            try:
                real_date2 = datetime.strptime(self.end_date, "%Y-%m-%d %H:%M:%S")
                return real_date2
            except ValueError as e:
                print(f"can't create datetime from date string!! {e}")
                return None
