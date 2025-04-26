import argparse
import logging
import sys

from map_app import create_app
from flask import Flask, send_from_directory
import threading


def run_tile_server():
    tile_app = Flask(__name__)
    @tile_app.route('/data/tiles/<path:filename>')
    def serve_tiles(filename):
        return send_from_directory('data/tiles', filename)
    tile_app.run(host='0.0.0.0', port=5000)

def run_main_app():
    create_app().run(host='0.0.0.0', port=1337, debug=False)

parser = argparse.ArgumentParser(description='Check for --tile_server argument')
parser.add_argument('--tile_server', action='store_true', help='Enable tile server')
args = parser.parse_args()


logging.basicConfig(level=logging.INFO, stream=sys.stdout)
if __name__ == "__main__":
    if args.tile_server:
        tile_server_thread = threading.Thread(target=run_tile_server)
        tile_server_thread.start()
        tile_server_thread.join()

    main_app_thread = threading.Thread(target=run_main_app)
    main_app_thread.start()
    main_app_thread.join()


