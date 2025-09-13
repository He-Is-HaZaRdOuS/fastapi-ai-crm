from sqlalchemy import event
from sqlmodel import Session, create_engine

from app.core.config import settings

engine = create_engine(settings.DB_URL, echo=True)

if settings.DB_URL.startswith("sqlite"):
    from sqlalchemy import text
    from sqlalchemy.engine import Engine

    with engine.begin() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL;"))

    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


# Dependency
def get_session():
    with Session(engine) as session:
        yield session
