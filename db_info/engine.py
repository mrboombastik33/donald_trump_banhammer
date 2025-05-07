from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import async_session, create_async_engine, AsyncSession, async_sessionmaker
from db_info.models import Base

DATABASE_NAME = 'database.db'

engine = create_async_engine(f'sqlite+aiosqlite:///{DATABASE_NAME}', echo = True)

session_maker = async_sessionmaker(bind = engine, class_ = AsyncSession, expire_on_commit = False)

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)




