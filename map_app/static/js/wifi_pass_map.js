//TODO hardcoded to czech republic
const map = L.map('map').setView([49.8175, 15.4730], 7);
const markers = L.markerClusterGroup();
const apiBaseUrl = '/api';
let AP_len_global = 0;
const getElementValue = (id) => document.getElementById(id)?.value.trim();

let remoteTileUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
L.control.locate({ drawCircle: false }).addTo(map);

// Set default OpenStreetMap tiles
L.tileLayer(remoteTileUrl, {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);


fetchDataAndUpdateMap(`${apiBaseUrl}/wifi_pass_map`);


// ----------------------------STATUS ---------------------------
function updateStatsDiv(script_statuses, AP_len) {
  let statsDiv = document.getElementById('stats-popup');
  if (!statsDiv) {
      statsDiv = document.createElement('div');
      statsDiv.id = 'stats-popup';
      statsDiv.style = `
        position: fixed; top: 10px; right: 10px;
        background-color: rgba(0, 0, 0, 0.7);
        color: white; padding: 10px; border-radius: 5px;
        z-index: 1000;
      `;
      document.body.appendChild(statsDiv);
  }

  AP_len_global = AP_len;

  script_statuses.forEach(script => {
        const scriptDiv = document.createElement('div');
        scriptDiv.textContent = `${script.name} ${script.len !== undefined ? `(${script.len})` : ''}`;
        scriptDiv.style.color = script.status === 'success' ? 'green' : script.status === 'empty' ? 'orange' : 'red';
        statsDiv.appendChild(scriptDiv);
    });

  document.body.appendChild(statsDiv);
}

//-------------------------MARKERS---------------------------------

function createMarker(poi) {
    const popupContent = `
        <strong>bssid:</strong> ${poi.bssid}<br>
        <strong>essid:</strong> ${poi.essid}<br>
        <strong>encryption:</strong> ${poi.encryption}<br>
        <strong>password:</strong> ${poi.password}<br>
        <strong>source:</strong> ${poi.source}<br>
        <button onclick="window.open('${generateGeoSchemeURL(poi.latitude, poi.longitude)}', '_blank')">Navigate to</button>
        <button onclick="generateQrCode('${generateWifiUriScheme(poi.essid, poi.encryption, poi.password)}')">Show QR</button><br>  
    `;

    return L.marker([poi.latitude, poi.longitude], {
        icon: L.icon({
            iconUrl: poi.password ? 'static/images/marker-icon-2x.png' : 'static/images/m.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34]
        })
    }).bindPopup(popupContent);
}


function updateMarkers(data, append = true) {
    if (!append) markers.clearLayers(); // Clear markers unless appending
    data.forEach(poi => markers.addLayer(createMarker(poi)));
    map.addLayer(markers);
}

//-------------FETCH DATA -------------------
function fetchDataAndUpdateMap(url) {
    fetch(url)
        .then(response => response.json())
        .then(({data, script_statuses, AP_len}) => {
            console.debug('Result:', data);
            updateStatsDiv(script_statuses, AP_len);
            updateMarkers(data);

        })
        .catch(error => console.error("Error fetching data:", error));
}

function searchAndRefreshMap() {
    const params = new URLSearchParams({
        network_type: getElementValue('networkType'),
        encryption: getElementValue('encryption'),
        name: getElementValue('searchInputName'),
        network_id: getElementValue('searchInputNetworkId'),
        limit: getElementValue('searchInputLimit')
    });

    const query = [...params.entries()].filter(([_, v]) => v).length ? '?' + params.toString() : '';
    fetchDataAndUpdateMap(`${apiBaseUrl}/explore${query}`);
}

document.getElementById('loadButton').addEventListener('click', () => {
    const filters = [
        `center_latitude=${getElementValue('center_lat')}`,
        `center_longitude=${getElementValue('center_long')}`,
        getElementValue('networkType') && `network_type=${getElementValue('networkType')}`,
        getElementValue('searchInputCenterLimit') && `center_limit=${encodeURIComponent(getElementValue('searchInputCenterLimit'))}`
    ].filter(Boolean);

    fetch(`${apiBaseUrl}/load_sqare?${filters.join('&')}`)
        .then(response => response.json())
        .then(({ data, script_statuses, AP_len }) => {
            updateStatsDiv(script_statuses, AP_len);
            updateMarkers(data, true); // Append markers
        })
        .catch(error => console.error('Error fetching data:', error));
});



// ---------------------EVENT LISTENERS--------------------
document.querySelectorAll('#searchInputName, #searchInputNetworkId').forEach(input => {
    input.addEventListener('keydown', event => {
        if (event.key === 'Enter') searchAndRefreshMap();
    });
});
document.getElementById('searchButton').addEventListener('click', searchAndRefreshMap);

map.on('click', event => {
    document.getElementById('center_lat').value = event.latlng.lat;
    document.getElementById('center_long').value = event.latlng.lng;
});


//----------------------HELP STRING FUNCTIONS-------------------------
function generateGeoSchemeURL(lat, lng) {
    return `geo:${lat},${lng}`;
}

function generateWifiUriScheme(ssid, encryption, password) {
  return `WIFI:S:${ssid};T:${encryption};P:${password};H:false;`;
}

function generateQrCode(wifiUri) {
    const qr = qrcode(0, 'M'); // Error correction level
    qr.addData(wifiUri);
    qr.make();
    window.open(qr.createDataURL(10, 0), '_blank');
}

