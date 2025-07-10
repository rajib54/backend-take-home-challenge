import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Add your app folder to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Alembic Config object
config = context.config

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import models and Base metadata
from app import models
from app.core.database import Base

# Set metadata for autogeneration
target_metadata = Base.metadata

# Get DB URL from environment
database_url = os.getenv("SQLALCHEMY_DATABASE_URL")

if not database_url:
    raise ValueError("SQLALCHEMY_DATABASE_URL is not set in environment")

# Set DB URL dynamically
config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
