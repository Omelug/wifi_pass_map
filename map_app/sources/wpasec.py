import csv
import datetime
import os
import sys
import requests
import sqlalchemy as sa
from alembic import op
from sqlalchemy import Column, String, UniqueConstraint, Table, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import DDL
from sqlalchemy import event

from map_app.tools.db import Base

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from formator.bssid import format_bssid
from map_app.tools.db import Session, users_table,engine,metadata

wpasec_table = Table('wpasec', metadata,
    Column('ap_mac', String, primary_key=True),
    Column('sta_mac', String, primary_key=True),
    Column('ssid', String),
    Column('password', String),
    Column('timestamp', String),
    UniqueConstraint('ap_mac', 'sta_mac', 'ssid', name='_ap_sta_ssid_uc'),
    extend_existing=True
)

class Wpasec(Base):
    __table__ = wpasec_table

inspector = inspect(engine)
columns = [col['name'] for col in inspector.get_columns('users')]

if 'wpasec_api_key' not in columns:
    ddl = DDL("ALTER TABLE users ADD COLUMN wpasec_api_key VARCHAR")
    event.listen(metadata, 'before_create', ddl)
    metadata.create_all(engine)

def csv_to_db(csv_content):
    total_networks = 0
    new_networks = 0
    duplicate_networks = 0

    csv_reader = csv.reader(csv_content.decode('utf-8').splitlines(), delimiter=':')

    for row in csv_reader:
        if len(row) == 4:
            total_networks += 1
            ap_mac, sta_mac, ssid, password = row

            with Session() as session:
                try:

                    new_entry = Wpasec(
                        ap_mac=format_bssid(ap_mac),
                        sta_mac=format_bssid(sta_mac),
                        ssid=ssid,
                        password=password,
                        timestamp=datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                    )
                    session.add(new_entry)
                    session.commit()

                    new_networks += 1
                    print(f"Added new network: {ssid}")
                except IntegrityError:
                    session.rollback()
                    duplicate_networks += 1
        else:
            raise ValueError(f"Invalid CSV row: {row}")

    print(f"Processed a total of {total_networks} networks, {new_networks} new networks, {duplicate_networks} were already known or duplicates.")

# Return the CSV content for further processing
def download_potfile(api_key):
    api_url = "https://wpa-sec.stanev.org/?api&dl=1"
    cookies = {'key': api_key}

    try:
        response = requests.get(api_url, cookies=cookies)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        raise Exception(f"HTTP Error: {e}")

# Function to get the API key based on username
def get_wpasec_key(username):
    with Session() as session:
        result = session.execute(
            sa.select(users_table.c.wpasec_api_key).where(users_table.c.username == username)
        ).fetchone()
        return result[0] if result else None  # Return the API key if found, else None


def get_map_data():

    return []

#update data from wp_sec
def wpasec_update(username):
    print("WPA-SEC: Starting data update")
    api_key = get_wpasec_key(username)

    if not api_key:
        print(f"No API key found for {username}")
        exit(1)
    try:
        csv_content = download_potfile(api_key)
        csv_to_db(csv_content)
    except Exception as e:
        print(f"An error occurred: {e}")
    print("WPA-SEC: Finished")

def get_tools():
    return {"wpasec_update": [wpasec_update,{"username",str}]}

if __name__ == "__main__":
    wpasec_update(sys.argv[1])
