import uuid as uuid_pkg
from sqlmodel import Field, SQLModel

class UUIDSQLModel(SQLModel):
    """
    Base class for UUID-based models.
    """
    id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )