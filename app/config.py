from dotenv import load_dotenv
import os

# Load .env variables into os.environ
load_dotenv()

# App settings
DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
