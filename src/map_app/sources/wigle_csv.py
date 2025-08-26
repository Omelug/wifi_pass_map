import configparser
import csv
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import requests

from map_app.source_core.MapSource import MapSource
from map_app.source_core.ToolSource import ToolGenerator
from map_app.sources.wigle import Wigle


def safe_float(val):
    try:
        return float(val)
    except (ValueError, TypeError) as e:
        logging.warning(f"Could not convert value to float: {val} ({e})")
        return 0.0


class WigleCSV(MapSource):
    __description__ = ("Load WPA3 APs data from a CSV file, which is downloaded with Wigle_download tool "
                       "Downloaded files from wigle are filterd in data/raw/wigle/csv (So it can effect other plugins!!!!!)")

    def __init__(self):
        super().__init__("wigle_csv")
        default_config = configparser.ConfigParser()
        default_config["wigle_csv"] =  {"csv_file_name": "wigle_csv"}
        self.create_config(self.config_path(), default_config)


    def get_map_data(self, filters: Optional[Dict[str, Any]] = None) -> list[dict[str, Any]]:
        config = configparser.ConfigParser()
        config.read(self.config_path())

        csv_file_name = config.get("wigle_csv", "csv_file_name")
        results = {}
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        csv_file_path = os.path.abspath(os.path.join(base_dir, f"data/raw/wigle/{csv_file_name}.csv"))

        with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip metadata row
            headers = next(reader)  # Use second row as headers
            for row in reader:
                row_dict = dict(zip(headers, row))
                if filters and not all(str(row_dict.get(k, "")) == str(v) for k, v in filters.items()):
                    continue
                mac = row_dict.get("MAC")
                first_seen = row_dict.get("FirstSeen")

                try:
                    ts = datetime.strptime(first_seen, "%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    logging.warning(f"Could not parse date '{first_seen}' for MAC '{mac}': {e}")
                    continue
                # Keep only the latest record per MAC
                if mac not in results or ts > results[mac]["_ts"]:
                    results[mac] = {
                        "bssid": mac,
                        "encryption": row_dict.get("AuthMode"),
                        "essid": row_dict.get("SSID"),
                        "password": None,
                        "latitude": safe_float(row_dict.get("CurrentLatitude", 0)),
                        "longitude": safe_float(row_dict.get("CurrentLongitude", 0)),
                        "_ts": ts  # internal, for comparison
                    }
        # Remove internal _ts before returning
        return [{k: v for k, v in ap.items() if k != "_ts"} for ap in results.values()]

    def update(self, limit=1):
        headers = {"Authorization": f"Basic {Wigle()._get_api_key()}"}
        transactions_url =  "https://api.wigle.net/api/v2/file/transactions"

        # 1. Fetch transaction list
        resp = requests.get(transactions_url, headers=headers)
        print("Wigle API response status code:", resp.status_code)
        print("Wigle API response text:", resp.text[:500])  # Print first 500 chars for brevity
        resp.raise_for_status()
        try:
            data = resp.json()
        except Exception as e:
            logging.warning("Failed to decode JSON from Wigle API response.")
            print("Failed to decode JSON from Wigle API response.")
            print("Response text:", resp.text)
            print("Error:", str(e))
            raise

        results = data.get("results", [])
        if not results:
            print("No transactions found.")
            return

        base_dir = Path(__file__).resolve().parents[3] / "data/raw/wigle/csv"
        base_dir.mkdir(parents=True, exist_ok=True)

        count = 0
        for entry in results:
            if count >= limit:
                break

            file_name = entry.get("fileName")
            trans_id = entry.get("transid")

            if not file_name or not trans_id:
                continue

            local_path = base_dir / file_name
            if local_path.exists():
                print(f"Already downloaded: {file_name}")
                continue

            # 4. Download file
            download_url = f"https://api.wigle.net/api/v2/file/csv/{trans_id}"
            print(f"Downloading {file_name} -> {local_path}")
            dl = requests.get(download_url, headers=headers, stream=True)
            dl.raise_for_status()

            with open(local_path, "wb") as f:
                for chunk in dl.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Saved: {local_path}")
            count += 1

    def get_tools(self):
        gen = ToolGenerator(self)
        gen.addParam(
            tool_name="wigle_csv",
            param_name="csv_file_name",
            description="Path to the CSV file containing AP data"
        )
        gen.add_run_fun(tool_name="wigle_download", run_fun=self.update)
        return gen.get_list()
