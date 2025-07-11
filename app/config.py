import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env or .env.test depending on env var or fallback
env_file = os.getenv("ENV_FILE", ".env")
env_path = Path(__file__).parent.parent / env_file
load_dotenv(dotenv_path=env_path, override=True)

DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))