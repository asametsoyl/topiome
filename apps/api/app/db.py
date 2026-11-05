from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime

from sqlalchemy import DateTime, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.types import TypeDecorator

from .config import settings

connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    future=True,
)

if settings.database_url.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):  # noqa: ANN001
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()


class UTCDateTime(TypeDecorator):
    """Timezone-aware UTC datetimes on every backend.

    SQLite drops tzinfo, so values came back naive and the API sent them without
    an offset; browsers then read them as local time (3 h off in Türkiye).
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):  # noqa: ANN001, ANN201
        if value is not None and value.tzinfo is not None:
            value = value.astimezone(UTC)
        return value

    def process_result_value(self, value, dialect):  # noqa: ANN001, ANN201
        if isinstance(value, datetime) and value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


BASELINE_REVISION = "0001"


def upgrade_db(target_engine=None) -> None:  # noqa: ANN001
    """Bring the schema to the latest Alembic revision.

    Databases created before Alembic was added (tables present, no
    ``alembic_version``) are stamped at the baseline first, then upgraded.
    """
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import inspect

    from . import models  # noqa: F401
    from .migrate import ALEMBIC_INI, patch_alembic

    patch_alembic()
    target = target_engine or engine
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", target.url.render_as_string(hide_password=False))
    config.attributes["configure_logger"] = False

    with target.begin() as connection:
        config.attributes["connection"] = connection
        tables = set(inspect(connection).get_table_names())
        if "users" in tables and "alembic_version" not in tables:
            command.stamp(config, BASELINE_REVISION)
        command.upgrade(config, "head")


def init_db() -> None:
    upgrade_db()
