import logging
from contextlib import contextmanager
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()
metadata = Base.metadata
engine = None
Session = None


def db_init(custom_engine=None):
    global engine, Session
    if custom_engine is not None:
        engine = custom_engine
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DATA_DIR = os.path.join(BASE_DIR, '..', '..', '..', 'data')
        os.makedirs(DATA_DIR, exist_ok=True)
        CENTRAL_DB = os.path.join(DATA_DIR, 'wifi_pass_map.db')
        engine = create_engine(f"sqlite:///{CENTRAL_DB}")
    Session = sessionmaker(bind=engine)
    metadata.create_all(engine)
    logging.info("Database initialized.")

@contextmanager
def get_db_connection():
    if Session is None:
        raise RuntimeError("Database not initialized. Call db_init() first.")
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
