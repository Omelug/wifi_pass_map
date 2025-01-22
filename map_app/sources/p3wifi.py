import os
import sys
from sqlalchemy import create_engine, exc, text
import configparser

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from formator.bssid import format_bssid, dec2mac, mac2dec
from map_app.tools.db import Session,engine,metadata

# ------------CONFIG----------------

# create default config if not exists
SOURCES_CONFIG_FILE = "map_app/sources/config"
os.makedirs(SOURCES_CONFIG_FILE, exist_ok=True)
config_file_path = f'{SOURCES_CONFIG_FILE}/p3wifi.ini'
if not os.path.exists(config_file_path):
    config = configparser.ConfigParser()

    config['MAIN'] = {
        'db_ip':"localhost",
        'db_user':"root",
        'db_pass':"new_password",
        'db_name':"p3wifi"
        }

    with open(config_file_path, 'w') as config_file:
        config.write(config_file)
    print(f"WPASEC configuration created {config_file_path}")


def get_map_data(filters=None):
    config = configparser.ConfigParser()
    config.read(config_file_path)

    db_user = config['MAIN']['db_user']
    db_pass = config['MAIN']['db_pass']
    db_ip = config['MAIN']['db_ip']
    db_name = config['MAIN']['db_name']

    engine = create_engine(
        f'mysql+mysqlconnector://{db_user}:{db_pass}@{db_ip}/{db_name}',
        connect_args={'charset': 'utf8', 'collation': 'utf8mb4_general_ci'}
    )
    try:
        with engine.connect() as connection:
            with open('map_app/sources/get_3wifi_data.sql', 'r') as file:
                sql_script = file.read()
            if filters:
                if 'bssid' in filters:
                    filters['bssid'] = mac2dec(filters['bssid'])
                sql_script = sql_script[:-1]  # Remove the trailing semicolon
                filter_conditions = " AND ".join([f"{key} = :{key}" for key in filters.keys()])
                sql_script += f" AND {filter_conditions} LIMIT 100;"
            else:
                sql_script = sql_script[:-1] + " LIMIT 100;"
            print(sql_script)
            result = connection.execute(text(sql_script), filters)
            rows = result.fetchall()
            #print(rows)
    except exc.SQLAlchemyError as e:
        print(f"An error occurred: {e}")
        return []
    return [
        {
            "bssid": dec2mac(row[0]),
            "essid": row[1],
            "password": row[2],
            "latitude": row[3],
            "longitude": row[4]
        }
        for row in rows
    ]
