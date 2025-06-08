import os
import tempfile
import pytest
from sqlalchemy import create_engine, Column, String, Integer
from map_app.source_core.db import Database

"""
class DBTestModel(Database("test").Base):
    __tablename__ = "test"
    id = Column(Integer, primary_key=True)
    val = Column(String)

@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    engine = create_engine(f"sqlite:///{path}")
    Database().db_init(engine)
    Database().Base.metadata.create_all(engine)
    yield
    Database().Base.metadata.drop_all(engine)
    engine.dispose()
    os.remove(path)"""