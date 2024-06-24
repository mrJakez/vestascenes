from __future__ import annotations

from typing import List
from Helper.RawHelper import RawHelper
# from api.Scenes import AbstractScene
from Scenes import AbstractScene
from sqlmodel import Field, SQLModel


class SceneInstanceModel(SQLModel, table=True):
    __tablename__ = "scene_instances"

    id: str = Field(default=None, primary_key=True)
    class_string: str
    start_date: str
    end_date: str
    raw: str
    priority: int
    is_active: bool

    def __init__(self, scene: AbstractScene):
        self.id = scene.id
        self.class_string = scene.scene_object.__class__.__name__
        self.raw = RawHelper.get_raw_string(scene.raw)
        self.start_date = scene.start_date
        self.end_date = scene.end_date
        self.priority = scene.priority
        self.is_active = True

    def get_raw_list(self) -> List:
        return RawHelper.get_raw_object(self.raw)
