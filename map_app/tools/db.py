import logging
import os
from contextlib import contextmanager

from sqlalchemy import Column, String, UniqueConstraint, Table
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)

#logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CENTRAL_DB = os.path.join(BASE_DIR,'..','..','data', 'wifi_pass_map.db')
db_exists = os.path.exists(CENTRAL_DB)

engine = create_engine(f"sqlite:///{CENTRAL_DB}")
Base = declarative_base()
metadata = Base.metadata
Session = sessionmaker(bind=engine)

if not db_exists:
    metadata.create_all(engine)
    print("CENTRAL database created.")

@contextmanager
def get_db_connection():
    """
    Context manager for database connection
    -> manual closing not needed
    """
    session = Session()
    try:
        yield session
    finally:
        session.close()


#---------------------Table_v0----------------------
# Table_v0 is typical table to make some functions more generic
# This is definition, in sources.py are some functions to work with this table
def create_table_v0_table(table_name):
    """
    Create a table for storing wifi data (same format for all sources)
    Table will be created in CENTRAL_DB
    """
    return Table(table_name, Base.metadata,
        Column('bssid', String, primary_key=True),
        Column('encryption', String),
        Column('essid', String),
        Column('password', String),
        Column('time', String),
        Column('latitude', String),
        Column('longitude', String),
        Column('last_locate_try', String),
        UniqueConstraint('bssid', 'essid', name=f'{table_name}_ap_sta_ssid_uc'),
        extend_existing=True
    )