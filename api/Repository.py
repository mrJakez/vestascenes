import typing
from datetime import datetime

from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine, select

from Models.ChatGPTHistoryModel import ChatGPTHistoryModel
from Models.SceneInstanceModel import SceneInstanceModel
from Models.SnapshotModel import SnapshotModel

from Helper.Logger import setup_custom_logger
logger = setup_custom_logger(__file__)

class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Repository(metaclass=SingletonMeta):
    _engine: Engine = None

    def create_tables(self):
        SQLModel.metadata.create_all(self.get_engine())

    def get_engine(self):
        if self._engine is None:
            logger.info("engine will be initialized")
            sqlite_file_name = "/database/vbcontrol.db"
            sqlite_url = f"sqlite:///{sqlite_file_name}"
            self._engine = create_engine(sqlite_url, echo=False)

        return self._engine

    def get_snapshots(self) -> typing.List[SnapshotModel]:
        with Session(self.get_engine()) as session:
            statement = select(SnapshotModel)
            results = session.exec(statement)
            snapshots = []

            for snapshot in results:
                snapshots.append(snapshot)

        return snapshots

    def store_snapshot(self, snapshot: SnapshotModel) -> bool:
        with Session(self.get_engine()) as session:
            statement = select(SnapshotModel).where(SnapshotModel.raw == snapshot.raw)
            results = session.exec(statement)

            if len(results.all()) > 0:
                logger.info(f"snapshot '{snapshot.title}' already exists")
                return False
            else:
                session.add(snapshot)
                session.commit()
                return True

    def get_chatgpt_history(self):
        with Session(self.get_engine()) as session:
            statement = select(ChatGPTHistoryModel).limit(200)
            results = session.exec(statement)
            models = []

            for model in results:
                models.append(model)

        return models

    def save_chatgpt_history(self, model: ChatGPTHistoryModel):
        with Session(self.get_engine()) as session:
            session.add(model)
            session.commit()
            session.refresh(model)

    def get_scene_instances(self):
        with Session(self.get_engine()) as session:
            statement = select(SceneInstanceModel)
            results = session.exec(statement)
            scene_instances = []

            for scene_instance in results:
                scene_instances.append(scene_instance)

        return scene_instance

    def save_scene_instance(self, model: SceneInstanceModel):
        with Session(self.get_engine()) as session:
            session.add(model)
            session.commit()

    def scene_instances_with_id_exists(self, given_id) -> bool:

        with Session(self.get_engine()) as session:
            statement = select(SceneInstanceModel).where(SceneInstanceModel.id == given_id)
            results = session.exec(statement)

            if len(results.all()) > 0:
                return True

        return False

    def get_active_scene_instance(self) -> typing.Optional[SceneInstanceModel]:
        with Session(self.get_engine()) as session:
            # noinspection PyPep8
            statement = select(SceneInstanceModel).where(SceneInstanceModel.is_active == True)
            results = session.exec(statement).all()
            count = len(results)

            if count == 0:
                return None

            for model in results:
                return model

    def get_suppressed_scene_instance(self) -> typing.Optional[SceneInstanceModel]:
        with Session(self.get_engine()) as session:
            # noinspection PyPep8
            statement = select(SceneInstanceModel).where(SceneInstanceModel.end_date > datetime.now()).where(SceneInstanceModel.is_active == False)
            results = session.exec(statement).all()
            count = len(results)

            if count == 0:
                return None
            else:
                return results[0]

    def unmark_active_scene_instance(self):
        with Session(self.get_engine()) as session:
            # noinspection PyPep8
            statement = select(SceneInstanceModel).where(SceneInstanceModel.is_active == True)
            results = session.exec(statement)

            for model in results.all():
                model.is_active = False
                session.add(model)
                session.commit()
                session.refresh(model)

    def mark_scene_instance_as_active(self, model: SceneInstanceModel):
        with Session(self.get_engine()) as session:
            model.is_active = True
            session.add(model)
            session.commit()
            session.refresh(model)
