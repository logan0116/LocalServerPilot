from sqlalchemy import Column, String, Integer
from app.db.base import Base, TimestampMixin


class ServerModel(Base, TimestampMixin):
    __tablename__ = "servers"

    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    ip = Column(String, nullable=False)
    port = Column(Integer, default=22)
    user = Column(String, nullable=False)
    password = Column(String, nullable=True)
    private_key = Column(String, nullable=True)
