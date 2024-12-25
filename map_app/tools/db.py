from contextlib import contextmanager
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, UniqueConstraint, Table, inspect
from sqlalchemy.exc import IntegrityError

Base = declarative_base()

CENTRAL_DB = 'data/wifi_pass_map.db'

engine = create_engine(f"sqlite:///{CENTRAL_DB}")
Session = sessionmaker(bind=engine)
metadata = MetaData()
metadata.reflect(bind=engine)

metadata.create_all(engine)

@contextmanager
def get_db_connection():
    conn = engine.connect()
    try:
        yield conn
    finally:
        conn.close()


def create_wifi_table(table_name):
    return Table(table_name, metadata,
        Column('bssid', String, primary_key=True),
        Column('encryption', String),
        Column('essid', String),
        Column('password', String),
        Column('time', String),
        Column('latitude', String),
        Column('longitude', String),
        UniqueConstraint('bssid', 'essid', name=f'{table_name}_ap_sta_ssid_uc'),
        extend_existing=True
    )
