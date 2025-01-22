import os
import re

from map_app.sources.wpasec import get_wpasec_key
from map_app.tools.db import CENTRAL_DB
from map_app.tools.wigle_api import get_api_key
from what_is_wrong.wiw import print_o, print_rg


# -------------MAIN ------------

def is_standard_key(key):
    # Regular expression for base64 encoded string
    base64_pattern = r'^[A-Za-z0-9+/=]+$'
    return bool(re.match(base64_pattern, key))


def is_hex_key(key):
    # Regular expression for a 32-character hexadecimal string
    hex_pattern = r'^[a-fA-F0-9]{32}$'
    return bool(re.match(hex_pattern, key.strip()))

if __name__ == "__main__":
    print_o("What is wrong with this code?")

    key = get_wpasec_key()
    print_rg(f"wpasec api key is: {key}", is_hex_key(key), "Key not in hex format")
    print_rg(f"Central database exists {CENTRAL_DB} ", os.path.exists(CENTRAL_DB))

    print_o("WPASEC modules")
    key = get_api_key()
    print_rg(f"Wigle api key is: {key}", is_standard_key(key), "Key not in base64 format")

