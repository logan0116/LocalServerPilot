from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.config import get_settings
import os

DATABASE_URL = os.getenv("LSP_DATABASE_URL", "sqlite+aiosqlite:///./lsp.db")


class Database:
    def __init__(self):
        self.engine = None
        self.session_factory = None

    def init(self, database_url: str = None):
        url = database_url or DATABASE_URL
        self.engine = create_async_engine(url, echo=False)
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def get_session(self) -> AsyncSession:
        async with self.session_factory() as session:
            yield session

    async def close(self):
        if self.engine:
            await self.engine.dispose()


database = Database()


async def get_db():
    async for session in database.get_session():
        yield session
