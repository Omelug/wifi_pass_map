import configparser
import os
import sqlite3
import glob
import json
import csv
import subprocess
from typing import Dict, Any, Optional

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from map_app.source_core.MapSource import MapSource
from map_app.source_core.ToolSource import ToolGenerator


class WigleDownload(MapSource):
    __description__ = "Tools to get localization for access point from wigle(https://wigle.net/)"

    def __init__(self):
        super().__init__("wigle_wpa3")

        default_config = configparser.ConfigParser()
        default_config['wigle_view'] = {
            'database_name': 'wigle_wpa3'
        }

        self.create_config(config=default_config)

    def __get_db_path(self):
        config = configparser.ConfigParser()
        config.read(self.config_path())
        db_name = config.get('wigle_view', 'database_name')
        return os.path.abspath(os.path.join(BASE_DIR, f"data/raw/wigle/{db_name}.db"))

    def __ensure_table(self, conn):
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wigle_networks
            (
                bssid      TEXT PRIMARY KEY,
                ssid       TEXT,
                encryption TEXT,
                trilat     REAL,
                trilong    REAL,
                country    TEXT,
                city       TEXT,
                lasttime   TEXT
            )
        """)
        conn.commit()

    def __get_csv_files(self):
        csv_dir = os.path.join(BASE_DIR, "data/raw/wigle/csv")
        return glob.glob(os.path.join(csv_dir, "*.csv"))

    def __import_csv_file(self, conn, csv_file):
        cursor = conn.cursor()
        total_inserted = 0
        with open(csv_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if len(lines) < 2:
                return 0
            # Use second line as header
            header = lines[1].strip().split(',')
            reader = csv.DictReader(lines[2:], fieldnames=header)
            for row in reader:
                cursor.execute("""
                    INSERT OR REPLACE INTO wigle_networks
                    (bssid, ssid, encryption, trilat, trilong, country, city, lasttime)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row.get('MAC'),
                    row.get('SSID'),
                    row.get('AuthMode'),
                    float(row.get('CurrentLatitude', 0)),
                    float(row.get('CurrentLongitude', 0)),
                    row.get('Country'),
                    row.get('City'),
                    row.get('FirstSeen')
                ))
                total_inserted += 1
        conn.commit()
        return total_inserted

    def wigle_csv_to_sql(self):
        import logging
        db_path = self.__get_db_path()
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        self.__ensure_table(conn)
        total_inserted = 0
        for csv_file in self.__get_csv_files():
            total_inserted += self.__import_csv_file(conn, csv_file)
        conn.close()
        logging.info(f"CSV import complete. Total APs imported: {total_inserted}")
        return total_inserted

    def filter_csv(self) -> None:
        csv_dir = os.path.join(BASE_DIR, "data/raw/wigle/csv")
        filter_json_path = os.path.join(csv_dir, "wpa3_filter.json")

        # Load filter status
        if os.path.exists(filter_json_path):
            with open(filter_json_path, "r") as f:
                filtered_files = set(json.load(f))
        else:
            filtered_files = set()

        csv_files = glob.glob(os.path.join(csv_dir, "*.csv"))
        for csv_file in csv_files:
            file_name = os.path.basename(csv_file)
            if file_name in filtered_files:
                continue

            filtered_rows = []
            # Copy first 2 lines, then filter for SAE|WPA3
            awk_cmd = (
                f"awk -F',' 'NR<=2 {{print; next}} $0 ~ /SAE|WPA3/ {{print}}' '{csv_file}' > '{csv_file}.tmp' && mv '{csv_file}.tmp' '{csv_file}'"
            )
            subprocess.run(awk_cmd, shell=True, check=True)

            filtered_files.add(file_name)

        with open(filter_json_path, "w") as f:
            json.dump(list(filtered_files), f)

        # Call CSV to SQL import after filtering
        self.wigle_csv_to_sql()

    def get_map_data(self, filters: Optional[Dict[str, Any]] = None) -> list[dict[str, Any]]:
        config = configparser.ConfigParser()
        config.read(self.config_path())
        db_name = config.get('wigle_view', 'database_name')
        db_path = os.path.abspath(os.path.join(BASE_DIR, f"data/raw/wigle/{db_name}.db"))

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = "SELECT bssid, ssid, encryption, trilat, trilong FROM wigle_networks"
        params = []
        if filters:
            clauses = []
            for key, value in filters.items():
                clauses.append(f"{key} = ?")
                params.append(value)
            if clauses:
                query += " WHERE " + " AND ".join(clauses)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        # Map columns to required output keys
        return [
            {
                "bssid": row[0],
                "encryption": row[2],
                "essid": row[1],
                "password": None,
                "latitude": row[3],
                "longitude": row[4]
            }
            for row in rows
        ]

    def get_tools(self):
        gen = ToolGenerator(self)
        gen.addParam(tool_name="wigle_view",
                     param_name="database_name",
                     description="Name of sql database in /data/raw/wigle/")
        gen.add_run_fun(tool_name="wigle_wpa3_filter", run_fun=self.filter_csv)
        return gen.get_list()
