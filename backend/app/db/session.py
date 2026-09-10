from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from app.core.config import get_settings


def build_engine(database_url: str | None = None) -> Engine:
    url = database_url or get_settings().database_url
    # Render exposes PostgreSQL URLs without a SQLAlchemy driver suffix. This
    # project uses psycopg (v3), so select it rather than the psycopg2 default.
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args, pool_pre_ping=True)
