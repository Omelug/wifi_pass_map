import os
import requests

# List of resources to download
resources = [
    # JavaScript files
    {"url": "https://unpkg.com/leaflet/dist/leaflet.js", "filename": "js/leaflet.js"},
    {"url": "https://cdn.jsdelivr.net/npm/leaflet.locatecontrol/dist/L.Control.Locate.min.js", "filename": "js/L.Control.Locate.min.js"},
    {"url": "https://cdnjs.cloudflare.com/ajax/libs/qrcode-generator/1.4.4/qrcode.min.js", "filename": "js/qrcode.min.js"},
    {"url": "https://unpkg.com/leaflet.markercluster/dist/leaflet.markercluster-src.js", "filename": "js/leaflet.markercluster-src.js"},
    {"url": "https://unpkg.com/leaflet/dist/leaflet.js.map", "filename": "js/leaflet.js.map"},
    {"url": "https://cdn.jsdelivr.net/npm/leaflet.locatecontrol/dist/L.Control.Locate.min.js.map", "filename": "js/L.Control.Locate.min.js.map"},
    {"url": "https://unpkg.com/leaflet.markercluster/dist/leaflet.markercluster-src.js.map", "filename": "js/leaflet.markercluster-src.js.map"},

    # CSS files
    {"url": "https://unpkg.com/leaflet/dist/leaflet.css", "filename": "css/leaflet.css"},
    {"url": "https://cdn.jsdelivr.net/npm/leaflet.locatecontrol/dist/L.Control.Locate.min.css", "filename": "css/L.Control.Locate.min.css"},
    {"url": "https://unpkg.com/leaflet.markercluster/dist/MarkerCluster.css", "filename": "css/MarkerCluster.css"},
    {"url": "https://unpkg.com/leaflet.markercluster/dist/MarkerCluster.Default.css", "filename": "css/MarkerCluster.Default.css"}
]

# Base directory for saving files
base_dir = "."

# Download each resource
for resource in resources:

    # Determine full path for the file
    file_path = os.path.join(base_dir, resource["filename"])
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure the directory exists

    # Download the resource
    try:
        response = requests.get(resource["url"], timeout=10)
        response.raise_for_status()  # Raise an error for HTTP issues
        with open(file_path, "wb") as file:
            file.write(response.content)
        print(f"Downloaded: {resource['url']} -> {file_path}")
    except requests.RequestException as e:
        print(f"Failed to download {resource['url']}: {e}")
