import os
import sys
from sqlalchemy import create_engine, exc, text
import configparser
from map_app.sources.sources import config_path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from formator.bssid import dec2mac, mac2dec

# ------------CONFIG----------------
if not os.path.exists(config_path()):
    config = configparser.ConfigParser()

    config['MAIN'] = {
        'db_ip':"localhost",
        'db_user':"root",
        'db_pass':"new_password",
        'db_name':"p3wifi"
        }

    with open(config_path(), 'w') as config_file:
        config.write(config_file)
    print(f"WPASEC configuration created {config_path()}")


def load_random_APs_to_limit(filters=None):
    with open('map_app/sources/get_3wifi_data.sql', 'r') as file:
        sql_script = file.read()
    limit = 100
    # print(filters)
    if filters:
        filter_conditions = ""
        if 'limit' in filters:
            limit = filters.pop('limit')
        sql_script = sql_script[:-1]
        if not filters:
            sql_script += f" LIMIT {limit};"
        else:
            # Remove the trailing semicolon
            if 'bssid' in filters:
                filter_conditions += f"nets.BSSID = {mac2dec(filters.pop('bssid'))} "
            filter_conditions += " AND ".join([f"{key} = :{key}" for key in filters.keys()])
            sql_script += f" AND {filter_conditions} LIMIT {limit};"
    else:
        return f"{sql_script[:-1]} LIMIT {limit};"
    # print(sql_script)
    return sql_script


def load_map_sqare(center_latitude,center_longitude, center_limit=None):
    if center_limit is None:
        center_limit = 0.05
    print(center_latitude,center_longitude,center_limit)
    print("\n\n")
    sql_script = f"""
        SELECT nets.BSSID, ESSID, WifiKey, geo.latitude, geo.longitude
        FROM nets
        JOIN geo ON nets.BSSID = geo.BSSID
        WHERE geo.latitude BETWEEN {center_latitude} - {center_limit} AND {center_latitude} + {center_limit}
          AND geo.longitude BETWEEN {center_longitude} - {center_limit} AND {center_longitude} + {center_limit}
        LIMIT 10000000;
    """
    print(sql_script)
    return sql_script

# --------------------Map Data --------------------
def get_map_data(filters=None):
    config = configparser.ConfigParser()
    config.read(config_path())

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
            print("Center", filters)
            if filters is not None and 'center_latitude' in filters and 'center_longitude' in filters:
                sql_script = load_map_sqare(
                    filters['center_latitude'],
                    filters['center_longitude'],
                    filters.get('center_limit')
                )
            else:
                sql_script = load_random_APs_to_limit(filters)

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
