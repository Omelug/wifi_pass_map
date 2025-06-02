import logging
from contextlib import contextmanager
import os
from typing import Any, Generator, Optional

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session as SessionType

Base: Any = declarative_base()
metadata = Base.metadata
engine: Optional[Engine] = None
SessionFactory: Optional[sessionmaker] = None

def db_init(custom_engine: Optional[Engine] = None) -> None:
    global engine, SessionFactory
    if custom_engine is not None:
        engine = custom_engine
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DATA_DIR = os.path.join(BASE_DIR, '..', '..', '..', 'data')
        os.makedirs(DATA_DIR, exist_ok=True)
        CENTRAL_DB = os.path.join(DATA_DIR, 'wifi_pass_map.db')
        engine = create_engine(f"sqlite:///{CENTRAL_DB}")
    SessionFactory = sessionmaker(bind=engine)
    metadata.create_all(engine)
    logging.info("Database initialized.")

@contextmanager
def get_db_connection() -> Generator[SessionType, None, None]:
    global SessionFactory
    if SessionFactory is None:
        raise RuntimeError("Database not initialized. Call db_init() first.")
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()