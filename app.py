import argparse
from map_app import create_app
from flask import Flask, send_from_directory

parser = argparse.ArgumentParser(description='Check for --tile_server argument')
parser.add_argument('--tile_server', action='store_true', help='Enable tile server')
args = parser.parse_args()

if __name__ == "__main__":
    #create_app().run(host='0.0.0.0', port=1337, debug=True)
    create_app().run(host='0.0.0.0', port=1337, debug=False)

    if args.tile_server:
        tile_app = Flask(__name__)
        @tile_app.route('/tiles/<path:filename>')
        def serve_tiles(filename):
            return send_from_directory('tiles', filename)
        tile_app.run(host='0.0.0.0', port=5000)
