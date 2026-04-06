from typing import List, Optional
import uuid
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.service_config import ServiceConfigModel


class ServiceConfigCRUD:
    @staticmethod
    def create(session: AsyncSession, name: str, start_command: str, stop_command: str,
               description: str = None, image_depend: List[str] = None,
               if_gpu: bool = False, allow_server: List[str] = None) -> ServiceConfigModel:
        config = ServiceConfigModel(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            image_depend=json.dumps(image_depend or []),
            if_gpu=if_gpu,
            allow_server=json.dumps(allow_server or []),
            start_command=start_command,
            stop_command=stop_command
        )
        session.add(config)
        return config

    @staticmethod
    async def get_all(session: AsyncSession) -> List[ServiceConfigModel]:
        result = await session.execute(select(ServiceConfigModel))
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(session: AsyncSession, config_id: str) -> Optional[ServiceConfigModel]:
        result = await session.execute(select(ServiceConfigModel).where(ServiceConfigModel.id == config_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update(session: AsyncSession, config_id: str, **kwargs) -> Optional[ServiceConfigModel]:
        config = await ServiceConfigCRUD.get_by_id(session, config_id)
        if not config:
            return None
        for key, value in kwargs.items():
            if value is not None:
                if key in ("image_depend", "allow_server") and isinstance(value, list):
                    value = json.dumps(value)
                if hasattr(config, key):
                    setattr(config, key, value)
        return config

    @staticmethod
    async def delete(session: AsyncSession, config_id: str) -> bool:
        config = await ServiceConfigCRUD.get_by_id(session, config_id)
        if not config:
            return False
        await session.delete(config)
        return True

    @staticmethod
    def parse_json_fields(config: ServiceConfigModel) -> dict:
        return {
            "image_depend": json.loads(config.image_depend or "[]"),
            "allow_server": json.loads(config.allow_server or "[]")
        }


service_config_crud = ServiceConfigCRUD()
