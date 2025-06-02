import os
import tempfile
import pytest
from sqlalchemy import create_engine, Column, String, Integer
from src.map_app.source_core import db

class DBTestModel(db.Base):
    __tablename__ = "test"
    id = Column(Integer, primary_key=True)
    val = Column(String)

@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    engine = create_engine(f"sqlite:///{path}")
    db.db_init(engine)
    db.Base.metadata.create_all(engine)
    yield
    db.Base.metadata.drop_all(engine)
    engine.dispose()
    os.remove(path)