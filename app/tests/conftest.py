import os
import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db, engine
from app.main import app
from fastapi.testclient import TestClient
from pathlib import Path

# Step 1: Load .env.test manually and confirm it loaded
env_path = Path(__file__).resolve().parent.parent.parent / ".env.test"
load_dotenv(dotenv_path=env_path, override=True)

# Step 2: Get and check DB URL
TEST_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

# Step 3: Setup engine
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def test_db(setup_test_db):
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def client(test_db):
    def override_get_db():
        yield test_db
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def clean_db():
    # Drop all tables and recreate before each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield