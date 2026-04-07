from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import os
from dotenv import load_dotenv
from app.database import Base
from app import models

config = context.config

load_dotenv()

config.set_main_option('sqlalchemy.url', os.environ['DATABASE_URL'])

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """
    Configure Alembic and run migrations using a URL-only (offline) context.
    
    Sets up the migration context with the configured SQLAlchemy URL, uses literal-bound parameters and named param style, and executes migrations inside a transaction without creating a DB engine or opening a DBAPI connection.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Configure Alembic with a live database connection and run migrations in online mode.
    
    Creates a SQLAlchemy connectable from the Alembic configuration, opens a connection, configures the migration context with that connection and the module's target metadata, and executes migrations inside a transaction.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
