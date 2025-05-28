import logging
import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CENTRAL_DB = os.path.join(BASE_DIR,'..','..','data', 'wifi_pass_map.db')
db_exists = os.path.exists(CENTRAL_DB)

engine = create_engine(f"sqlite:///{CENTRAL_DB}")
Base = declarative_base()
metadata = Base.metadata
Session = sessionmaker(bind=engine)

if not db_exists:
    metadata.create_all(engine)
    logging.info("CENTRAL database created.")

@contextmanager
def get_db_connection():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
