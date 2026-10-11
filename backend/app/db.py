from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import settings

class Base(DeclarativeBase):
    pass

engine = create_engine(settings.database_url, pool_pre_ping=True, pool_timeout=5, connect_args={"connect_timeout": 5, "options": "-c statement_timeout=10000"})
Session = sessionmaker(engine, expire_on_commit=False)

def get_db():
    with Session() as db:
        yield db
