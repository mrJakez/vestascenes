from __future__ import annotations

from datetime import datetime
from typing import List, Any

from sqlmodel import Field, SQLModel

from Helper.RawHelper import RawHelper
# from api.Scenes import AbstractScene
from Scenes import AbstractScene

from Helper.Logger import setup_custom_logger
from Scenes.AbstractScene import SceneExecuteReturn

logger = setup_custom_logger(__file__)

class SceneInstanceModel(SQLModel, table=True):
    __tablename__ = "scene_instances"

    id: str = Field(default=None, primary_key=True)
    class_string: str
    start_date: str
    end_date: str
    overwritable: bool
    raw: str
    priority: int
    is_active: bool

    def __init__(self, scene_exec_return: SceneExecuteReturn, **data: Any):
        super().__init__(**data)
        self.id = scene_exec_return.id
        self.class_string = scene_exec_return.scene_object.__class__.__name__
        self.raw = RawHelper.get_raw_string(scene_exec_return.raw)
        self.start_date = scene_exec_return.start_date
        self.overwritable = scene_exec_return.scene_object.overwritable
        self.end_date = scene_exec_return.end_date
        self.priority = scene_exec_return.priority
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
                logger.error(f"can't create datetime from date string!! {e}")
                return None
