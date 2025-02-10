from what_is_wrong.wiw import print_o, print_rg
from map_app.tools.wigle_api import get_api_key
import re

if __name__ == "__main__":
    print_o("What is wrong with wigle module?")

def is_standard_key(key):
    # Regular expression for base64 encoded string
    base64_pattern = r'^[A-Za-z0-9+/=]+$'
    return bool(re.match(base64_pattern, key))

def wiw_wigle_connection():
    return None

def wiw_wigle_local():
    print_o("WPASEC modules")
    key = get_api_key()
    print_rg(f"Wigle api key is: {key}", is_standard_key(key), "Key not in base64 format")
