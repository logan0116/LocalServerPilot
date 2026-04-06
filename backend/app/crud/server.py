from typing import List, Optional
import uuid
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.server import ServerModel


class ServerCRUD:
    @staticmethod
    def create(session: AsyncSession, name: str, ip: str, user: str, 
               port: int = 22, password: str = None, private_key: str = None) -> ServerModel:
        server = ServerModel(
            id=str(uuid.uuid4()),
            name=name,
            ip=ip,
            port=port,
            user=user,
            password=password,
            private_key=private_key
        )
        session.add(server)
        return server

    @staticmethod
    async def get_all(session: AsyncSession) -> List[ServerModel]:
        result = await session.execute(select(ServerModel))
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(session: AsyncSession, server_id: str) -> Optional[ServerModel]:
        result = await session.execute(select(ServerModel).where(ServerModel.id == server_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update(session: AsyncSession, server_id: str, **kwargs) -> Optional[ServerModel]:
        server = await ServerCRUD.get_by_id(session, server_id)
        if not server:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(server, key):
                setattr(server, key, value)
        return server

    @staticmethod
    async def delete(session: AsyncSession, server_id: str) -> bool:
        server = await ServerCRUD.get_by_id(session, server_id)
        if not server:
            return False
        await session.delete(server)
        return True


server_crud = ServerCRUD()
