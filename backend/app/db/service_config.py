from sqlalchemy import Column, String, Boolean, Text
from app.db.base import Base, TimestampMixin


class ServiceConfigModel(Base, TimestampMixin):
    __tablename__ = "service_configs"

    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    image_depend = Column(Text, nullable=True)
    if_gpu = Column(Boolean, default=False)
    allow_server = Column(Text, nullable=True)
    start_command = Column(String, nullable=False)
    stop_command = Column(String, nullable=False)
