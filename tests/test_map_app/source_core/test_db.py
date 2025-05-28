import os
import tempfile
import pytest
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from map_app.source_core import db

Base = declarative_base()

class DBTestModel(Base):
    __tablename__ = "test"
    id = Column(Integer, primary_key=True)
    val = Column(String)

@pytest.fixture
def temp_db(monkeypatch):
    fd, path = tempfile.mkstemp()
    os.close(fd)
    engine = create_engine(f"sqlite:///{path}")
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    monkeypatch.setattr(db, "engine", engine)
    monkeypatch.setattr(db, "Session", Session)
    yield
    os.remove(path)

def test_get_db_connection_commit(temp_db):
    with db.get_db_connection() as session:
        obj = DBTestModel(val="ok")
        session.add(obj)
    with db.get_db_connection() as session:
        result = session.query(DBTestModel).first()
        assert result.val == "ok"

def test_get_db_connection_rollback(temp_db):
    with pytest.raises(Exception):
        with db.get_db_connection() as session:
            obj = DBTestModel(val="fail")
            session.add(obj)
            raise Exception("fail")
    with db.get_db_connection() as session:
        result = session.query(DBTestModel).filter_by(val="fail").first()
        assert result is None