import os
import re

from map_app.source_core.db import CENTRAL_DB
from map_app.sources.wpasec import Wpasec
from what_is_wrong import wigle_wiw
from what_is_wrong.wiw import print_o, print_rg


# -------------MAIN ------------


def is_hex_key(key):
    # Regular expression for a 32-character hexadecimal string
    hex_pattern = r'^[a-fA-F0-9]{32}$'
    return bool(re.match(hex_pattern, key.strip()))


def wiw_wpa_sec_local():
    key = Wpasec.__get_wpasec_key()
    print_rg(f"wpasec api key is: {key}", is_hex_key(key), "Key not in hex format")
    print_rg(f"Central database exists {CENTRAL_DB} ", os.path.exists(CENTRAL_DB))


def wiw_wpa_sec_connection():
    pass

if __name__ == "__main__":
    print_o("What is wrong with this code?")

    wiw_wpa_sec_local()
    wiw_wpa_sec_connection()

    wigle_wiw.wiw_wigle_local()
    wigle_wiw.wiw_wigle_connection()


