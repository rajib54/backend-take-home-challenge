# conftest.py
import os
import pytest
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# 1. Load .env.test before importing app modules or database config
env_path = Path(__file__).parent.parent.parent / ".env.test"
load_dotenv(dotenv_path=env_path, override=True)

# Now import app modules so they pick up the test env vars
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from app.core.database import Base, get_db
from app.main import app
from httpx import AsyncClient

# 2. Setup async engine & session for test DB from loaded env
TEST_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
engine_test = create_async_engine(TEST_DATABASE_URL, future=True, echo=False)
AsyncSessionLocal = async_sessionmaker(engine_test, expire_on_commit=False, class_=AsyncSession)

# 3. Create/drop schema once per test session
@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def async_test_db():
    async with AsyncSessionLocal() as session:
        # Clean all tables inside the same session before test runs
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(text(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE'))
        await session.commit()
        yield session

# 6. Override FastAPI get_db dependency with async test DB session
@pytest.fixture(scope="function")
async def async_client(async_test_db: AsyncSession):
    async def override_get_db():
        yield async_test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client

# 7. Provide asyncio event loop for pytest-asyncio
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
