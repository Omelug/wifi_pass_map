import secrets
import sys

import bcrypt
from sqlalchemy import create_engine, Column, String, Table, MetaData, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

CENTRAL_DB = 'data/wifi_pass_map.db'

engine = create_engine(f"sqlite:///{CENTRAL_DB}")
Session = sessionmaker(bind=engine)
metadata = MetaData()
metadata.reflect(bind=engine)

metadata.create_all(engine)