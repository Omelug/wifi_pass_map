import os
import pytest
from formator.bssid import format_bssid
from map_app.source_core import db
from map_app.source_core.Table_v0 import Table_v0
from map_app.source_core.db import Database


class Example_Tablev0(Table_v0):
    def __init__(self):
        super().__init__("test_tablev0_table")

class Example_Tablev0_2(Table_v0):
    def __init__(self):
        super().__init__("test_tablev0_2_table")

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    Database()
    yield
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TESTS_DIR = os.path.join(BASE_DIR, '..', '..', '..', 'tests')
    os.makedirs(TESTS_DIR, exist_ok=True)
    central_db = os.path.join(TESTS_DIR, 'test_database.db')

    db.Database._instances = {}
    Example_Tablev0._instances = {}
    Example_Tablev0_2._instances = {}
    if os.path.exists(central_db):
        os.remove(central_db)

    # --------- get_tablev0_tables ------------
    #TODO this test remode for test env
    """
    def test_get_tablev0_tables():
        test_table = Example_Tablev0()
        test_table2 = Example_Tablev0_2()

        names = Table_v0.get_tablev0_tables()
        assert set(names) == {test_table.SOURCE_NAME, test_table2.SOURCE_NAME}
    """""
# --------- _save_AP_to_db ------------
def test_save_duplicate_AP_to_db():
    test_table = Example_Tablev0()
    with Database().get_db_connection() as session:
        result1 = test_table._save_AP_to_db(
            bssid="AA:BB:CC:DD:EE:FF",
            essid="TestESSID",
            password="password123",
            time="2024-01-01 00:00:00",
            session=session
        )
        result2 = test_table._save_AP_to_db(
            bssid="AA:BB:CC:DD:EE:FF",
            essid="TestESSID",
            password="password123",
            time="2024-01-01 00:00:00",
            session=session
        )
        assert result1 is True
        assert result2 is False  # Duplicate

def test_save_AP_to_db_with_bssid_format():
    test_table = Example_Tablev0()
    with Database().get_db_connection() as session:
        raw_bssid = "aabbccddeeff"
        formatted_bssid = format_bssid(raw_bssid)
        result = test_table._save_AP_to_db(
            bssid=raw_bssid,
            essid="TestESSID2",
            password="password456",
            time="2024-01-02 00:00:00",
            bssid_format=True,
            session=session
        )
        # Check that the formatted bssid is in the table
        row = session.execute(
            test_table.table.select().where(test_table.table.c.bssid == formatted_bssid)
        ).first()
        assert result is True
        assert row is not None
        assert row.bssid == formatted_bssid

def test_save_AP_to_db_missing_bssid():
    test_table = Example_Tablev0()
    with Database().get_db_connection() as session:
        with pytest.raises(Exception):
            test_table._save_AP_to_db(
                bssid=None,
                essid="TestESSID3",
                password="password789",
                time="2024-01-03 00:00:00",
                session=session
            )

# --------- _save_AP_to_db ------------
