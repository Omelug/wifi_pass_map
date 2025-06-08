import logging
from contextlib import contextmanager
import os
from typing import Any, Generator, Optional, LiteralString

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session as SessionType


class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    @property
    def Base(self):
        return self._Base

    @property
    def metadata(self):
        return self._Base.metadata

    @property
    def engine(self):
        return self._engine

    @property
    def SessionFactory(self):
        return self._SessionFactory

    def __init__(self, central_db=None):
        if not hasattr(self, "_Base"):
            self._Base = declarative_base()
        if not hasattr(self, "_engine"):
            self._engine = None
        if not hasattr(self, "_SessionFactory"):
            self._SessionFactory = None
        self.db_init(central_db=central_db)

    def db_init(self, custom_engine: Optional[Engine] = None, central_db: LiteralString | None = None) -> None:
        if custom_engine is not None:
            self._engine = custom_engine
        else:
            if central_db is None:
                if "PYTEST_CURRENT_TEST" in os.environ:
                    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
                    TESTS_DIR = os.path.join(BASE_DIR, '..', '..', '..', 'tests')
                    os.makedirs(TESTS_DIR, exist_ok=True)
                    central_db = os.path.join(TESTS_DIR, 'test_database.db')
                else:
                    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
                    DATA_DIR = os.path.join(BASE_DIR, '..', '..', '..', 'data')
                    os.makedirs(DATA_DIR, exist_ok=True)
                    central_db = os.path.join(DATA_DIR, 'wifi_pass_map.db')
            self._engine = create_engine(f"sqlite:///{central_db}")
        self._SessionFactory = sessionmaker(bind=self.engine)
        self.metadata.create_all(self.engine)
        logging.info("Database initialized.")

    @contextmanager
    def get_db_connection(self) -> Generator[SessionType, None, None]:
        if self.SessionFactory is None:
            raise RuntimeError("Database not initialized. Call db_init() first.")
        session = self.SessionFactory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()