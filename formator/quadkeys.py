import mercantile
import pandas as pd
from sqlalchemy import create_engine
from math import sin, radians, atanh
from math import pi, atan, sinh, degrees
MAX_ZOOM_LEVEL=23



def bigint_to_quadkey(bigint): #remove '0b' prefix, make sure its even
    quadkey = bin(bigint)[2:]
    return quadkey.zfill((len(quadkey) + 1) // 2 * 2)


def bigint_to_quadkey_zoom(bigint, zoom_level):
    # Convert bigint to binary string
    binary_str = bin(bigint)[2:].zfill(zoom_level * 2)

    # Initialize quadkey
    quadkey = ''

    # Convert binary string to quadkey
    for i in range(zoom_level):
        digit = 0
        if binary_str[2 * i] == '1':
            digit += 1
        if binary_str[2 * i + 1] == '1':
            digit += 2
        quadkey += str(digit)

    return quadkey

def bigint_to_quadkey2(bigint, zoom_level):
    # Convert bigint to binary string
    binary_str = bin(bigint)[2:].zfill(zoom_level * 2)

    # Initialize quadkey
    quadkey = ''

    # Convert binary string to quadkey
    for i in range(zoom_level):
        digit = 0
        if binary_str[2 * i] == '1':
            digit += 1
        if binary_str[2 * i + 1] == '1':
            digit += 2
        quadkey += str(digit)

    return quadkey
def quadkey_to_tile(quadkey=None, big_int_qk=None, zoom_level=None):
    if big_int_qk is not None:
        quadkey= bigint_to_quadkey_zoom(big_int_qk, zoom_level)
    tile_x = 0
    tile_y = 0
    zoom = len(quadkey) // 2

    for i in range(zoom):
        bit = zoom - i - 1
        mask = 1 << bit
        if quadkey[2 * i] == '1':
            tile_x |= mask
        if quadkey[2 * i + 1] == '1':
            tile_y |= mask
    return tile_x, tile_y, zoom

def get_quadkeys_db():
    query = "SELECT DISTINCT quadkey FROM geo LIMIT 100"
    return pd.read_sql(query, engine)['quadkey'].tolist()

# Function to generate quadkeys for a given bounding box
def generate_quadkeys(bbox, zoom_level):
    min_lon, min_lat, max_lon, max_lat = bbox
    quadkeys = set()
    for tile in mercantile.tiles(min_lon, min_lat, max_lon, max_lat, zoom_level):
        quadkey = mercantile.quadkey(tile)
        quadkeys.add(quadkey)
    return quadkeys

def clip(value, min_value, max_value):
    return min(max(value, min_value), max_value)

#------------------Conversions------------------------------
def lat_to_tile_y(latitude, zoom):
    latitude = clip(latitude, -85.05112878, 85.05112878)
    sin_lat = sin(radians(latitude))
    e = 0.0818191908426  # eccentricity of the Earth
    y = 0.5 - (atanh(sin_lat) - e * atanh(e * sin_lat)) / (2 * pi)
    size_in_tiles = 1 << zoom
    return min(int(y * size_in_tiles), size_in_tiles - 1)

def tile_y_to_lat(tile_y, zoom):
    n = pi - 2.0 * pi * tile_y / (1 << zoom)
    return degrees(atan(sinh(n)))

def lon_to_tile_x(longitude, zoom):
    longitude = clip(longitude, -180, 180)
    x = (longitude + 180) / 360
    size_in_tiles = 1 << zoom
    return min(int(x * size_in_tiles), size_in_tiles - 1)

def tile_x_to_lon(tile_x, zoom):
    return tile_x / (1 << zoom) * 360.0 - 180.0

def tile_to_quadkey(tile_x, tile_y, zoom):
    if zoom == 0:
        return 0

    quadkey = ''
    for i in range(zoom):
        quadkey = str((tile_y & 1)) + str((tile_x & 1)) + quadkey
        tile_x >>= 1
        tile_y >>= 1
    return quadkey

def latlon_to_quadkey(latitude, longitude, zoom):
    if zoom == 0:
        return 0

    tile_x = lon_to_tile_x(longitude, zoom)
    tile_y = lat_to_tile_y(latitude, zoom)
    return tile_to_quadkey(tile_x, tile_y, zoom)
#-----------------------------------------------------

def get_quadkey(lat, long):
    return int(latlon_to_quadkey(lat, long, MAX_ZOOM_LEVEL),2)

def get_quadkey_bbox(bigint):
    tile_x, tile_y, zoom = quadkey_to_tile(bigint_to_quadkey(bigint))
    return [
        [tile_y_to_lat(tile_y, zoom), tile_x_to_lon(tile_x, zoom)],
        [tile_y_to_lat(tile_y + 1, zoom), tile_x_to_lon(tile_x + 1, zoom)]
    ]