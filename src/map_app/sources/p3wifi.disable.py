import configparser
import json
import os
import subprocess
import sys
from typing import Dict, Any, Optional

import requests
from IPython.testing.tools import default_config

from map_app.source_core.MySQL_Source import MySQL_MapSource
from map_app.source_core.PGSQL_Source import PGSQL_MapSource

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

#update = False
#path_to_sql = os.path.abspath("../../../data/raw/p3wifi_dump_19.05.2024.sql")
#psql_path_to_sql = os.path.abspath("../../../data/raw/psql_p3wifi_dump_19.05.2024.sql")

from sqlalchemy import create_engine, text

"""
def create_db_if_not_exists(host, user, password, dbname, port=5432):
    url = f"postgresql://{user}:{password}@{host}:{port}/postgres"
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            exists = conn.execute(text("SELECT 1 FROM pg_database WHERE datname=:db"), {'db': dbname}).scalar()
            if exists:
                print(f"Database '{dbname}' already exists")
                return True
        # New connection for CREATE DATABASE with autocommit
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            conn.execute(text(f'CREATE DATABASE "{dbname}"'))
            print(f"Database '{dbname}' created")
            return True
    except OperationalError as e:
        print("Error:", e)
        return False


def check_psql_connection_sa(host, user, password, dbname, port=5432):
    url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            print("PostgreSQL connection successful")
            return True
    except OperationalError as e:
        print("PostgreSQL connection failed:", e)
        return False

# Usage
create_db_if_not_exists(psql_db_ip, psql_db_user, psql_db_pass, psql_db_name)
if not check_psql_connection_sa(psql_db_ip, psql_db_user, psql_db_pass, psql_db_name):
    exit(42)
"""

"""
def update_p3wifi_mysql():
    conn = mysql.connector.connect(
        host=db_ip,
        user=db_user,
        password=db_pass
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")
    cursor.close()
    conn.close()

    # Add --force to continue on errors
    cmd = f"mysql -h {db_ip} -u {db_user} -p'{db_pass}' --force {db_name} < {path_to_sql}"
    print(cmd)
    #FIXME os.system(cmd)
    
     #TODO
        # self.check_db_connection_and_tables(
        #    {
        #        'nets': ['BSSID', 'ESSID', 'WiFiKey'],
        #        'geo': ['BSSID', 'latitude', 'longitude']
        #    }
        #)


def update_p3wifi_psql():
    cmd = f"pgloader mysql://{mysql_conn} postgresql://{psql_conn}"
    print(cmd)
    #TODO os.system(cmd)

# BE PATIENT, TOOL 15+ minutes
print("Update mysql p3wifi")
update_p3wifi_mysql()

# BE PATIENT, TOOL 15+ minutes
print("Update postgresql p3wifi")
update_p3wifi_psql()
"""



# ------------CONFIG----------------
class p3wifi(MySQL_MapSource, PGSQL_MapSource):


    def __init__(self):
        self.SCHEMA_NAME = "p3wifi"

        default_config = configparser.ConfigParser()
        default_config[self.SCHEMA_NAME] = {
            'country': '',
            'out_schema': 'p3wifi_cut_of',
        }

        MySQL_MapSource.__init__(self,self.SCHEMA_NAME, config=default_config)
        PGSQL_MapSource.__init__(self,self.SCHEMA_NAME)
        #check requiered tables



    # --------------------Map Data --------------------
    """
    def get_map_data(self, filters=None):
        try:
            with self._get_db_connection() as connection:
                if filters and 'center_latitude' in filters and 'center_longitude' in filters:
                    sql_script = self.__load_map_square(
                        filters['center_latitude'],
                        filters['center_longitude'],
                        filters.get('center_limit', 0.05)
                    )
                else:
                    sql_script = self.__load_random_APs_to_limit(filters)

                rows = connection.execute(text(sql_script), filters).fetchall()

        except exc.SQLAlchemyError as e:
            logging.error(f"An error occurred: {e}")
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
    """

    def get_map_data(self, filters: Optional[Dict[str, Any]] = None) -> list[dict[str, Any]]:
        pass

    @staticmethod
    def __download_geojson(country):
        url = f"https://www.geoboundaries.org/api/current/gbOpen/{country}/ADM1/"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Simplify: keep only geometry and shapeName
        features = []
        for feature in data.get('features', []):
            simplified = {
                "type": "Feature",
                "geometry": feature["geometry"],
                "properties": {
                    "name": feature["properties"].get("shapeName", "")
                }
            }
            features.append(simplified)

        simple_geojson = {
            "type": "FeatureCollection",
            "features": features
        }

        # Save to file for PostGIS import
        with open(f"../../data/clean/{country}_adm1_simple.geojson", "w") as f:
            json.dump(simple_geojson, f)

        return simple_geojson

    def __enable_postgis(self, dbname=None):
        engine = create_engine(PGSQL_MapSource.connection_link(self,dbname=dbname))
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))

    def __import_geojson_to_postgis(self, out_schema, country):
        schema_name = f"p3wifi_{country}"
        ogr_cmd = [
            "ogr2ogr",
            "-f", "PostgreSQL",
            PGSQL_MapSource.connection_link(self,eq_str=True) ,
            f"../../data/clean/{country}_adm1_simple.geojson",
            "-nln", f"{schema_name}.{table}",
            "-nlt", "MULTIPOLYGON",
            "-lco", f"SCHEMA={schema_name}",
            "-lco", "GEOMETRY_NAME=geom",
            "-lco", "FID=id",
            "-overwrite"
        ]
        subprocess.run(ogr_cmd, check=True)

    def _cut_of_db(self):
        config = configparser.ConfigParser()
        config.read(self.config_path())
        self.__download_geojson(country=config[self.SOURCE_NAME]['country'])
        self.__enable_postgis()
        self.__import_geojson_to_postgis(
            table="p3wifi",
            out_schema=config[self.SOURCE_NAME]['out_schema'],
            country=config[self.SOURCE_NAME]['country']
        )

    def get_tools(self) -> Dict[str, Dict[str, Any]] | None:
        from map_app.source_core.ToolSource import ToolGenerator
        gen = ToolGenerator(self)
        gen.addParam(tool_name="cut_of_databse", param_name="country", description="country code ISO-3166-1")
        gen.addParam(tool_name="cut_of_databse", param_name="out_database",
                     description="out database, same for override")
        gen.add_run_fun("cut_of_databse", self._cut_of_db)
        # Add DEFAULT_SOURCE_NAME with empty params
        result = gen.get_list()
        result[self.DEFAULT_SOURCE_NAME] = {"params": []}
        return result