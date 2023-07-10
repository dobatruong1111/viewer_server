import uuid

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# @as_declarative()
class BaseModel(Base):
    __abstract__ = True

    # id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # id = Column(Integer, primary_key=True, index=True)
    id = Column(String, primary_key=True, index=True)
    __name__: str

    # Generate __tablename__ automatically
    # @declared_attr
    # def __tablename__(cls) -> str:
    #     return cls.__name__.lower()
