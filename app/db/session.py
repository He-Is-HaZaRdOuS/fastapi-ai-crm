from sqlmodel import Session, create_engine

from app.core.config import settings

engine = create_engine(settings.DB_URL, echo=True)


# Dependency
def get_session():
    with Session(engine) as session:
        yield session
