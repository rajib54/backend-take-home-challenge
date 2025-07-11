# app/core/database.py

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

# Dependency for FastAPI routes and services
async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
