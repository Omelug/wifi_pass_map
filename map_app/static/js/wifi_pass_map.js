function generateGeoSchemeURL(latitude, longitude) {
  return `geo:${latitude},${longitude}`;
}

function generateWifiUriScheme(ssid, encryption, password) {
  return `WIFI:S:${ssid};T:${encryption};P:${password};H:false;`;
}

function generateQrCode(wifiUri) {
  const qr = qrcode(0, 'M'); // Error correction level
  qr.addData(wifiUri);
  qr.make();
  const qrCodeUrl = qr.createDataURL(10, 0); // size, margin
  window.open(qrCodeUrl, '_blank');
}
let AP_len_global = 0;
function createStatsDiv(script_success, script_count_all, AP_len, script_statuses) {
  const statsDiv = document.createElement('div');
  statsDiv.id = 'stats-popup';
  statsDiv.style = `
    position: fixed;
    top: 10px;
    right: 10px;
    background-color: rgba(0, 0, 0, 0.7);
    color: white;
    padding: 10px;
    border-radius: 5px;
    z-index: 1000;
  `;
  AP_len_global = AP_len;
  statsDiv.innerHTML = `Scripts: ${script_success}/${script_count_all} APs: ${AP_len}<br>`;

  script_statuses.forEach(script => {
    const scriptDiv = document.createElement('div');
    scriptDiv.textContent = script.name;
    scriptDiv.style.color = script.status === 'success' ? 'green' : (script.status === 'empty' ? 'orange' : 'red');
    statsDiv.appendChild(scriptDiv);
  });

  document.body.appendChild(statsDiv);
}
function updateStatsDiv(script_success, script_count_all, AP_len, script_statuses) {
  const statsDiv = document.getElementById('stats-popup');
  if (!statsDiv) {
    createStatsDiv(script_success, script_count_all, AP_len, script_statuses);
    return;
  }
  AP_len_global += AP_len;
  statsDiv.innerHTML = `Scripts: ${script_success}/${script_count_all} APs: ${AP_len_global}<br>`;

  script_statuses.forEach(script => {
    const scriptDiv = document.createElement('div');
    scriptDiv.textContent = script.name;
    scriptDiv.style.color = script.status === 'success' ? 'green' : (script.status === 'empty' ? 'orange' : 'red');
    statsDiv.appendChild(scriptDiv);
  });
}

function createMarker(poi) {
  const geoSchemeURL = generateGeoSchemeURL(poi.latitude, poi.longitude);
  poi.wifiUri = generateWifiUriScheme(poi.essid, poi.encryption, poi.password);

  const popupContent = `
    <strong>bssid:</strong> ${poi.bssid}<br>
    <strong>essid:</strong> ${poi.essid}<br>
    <strong>encryption:</strong> ${poi.encryption}<br>
    <strong>password:</strong> ${poi.password}<br>
    <strong>source:</strong> ${poi.source}<br>
    <button onclick="window.open('${geoSchemeURL}', '_blank')">Navigate to</button>
    <button onclick="generateQrCode('${poi.wifiUri}')">Show QR</button><br>  
  `;

  const customIcon = L.icon({
    iconUrl: 'static/images/marker-icon-2x.png',
    iconSize: [25, 41], // size of the icon
    iconAnchor: [12, 41], // point of the icon which will correspond to marker's location
    popupAnchor: [1, -34] // point from which the popup should open relative to the iconAnchor
  });

  return L.marker([poi.latitude, poi.longitude], { icon: customIcon }).bindPopup(popupContent);
}

//TODO hardcoded to czech republic
const map = L.map('map').setView([49.8175, 15.4730], 7);

//TODO create possibility to get data from openstreetmap data on local

function checkLocalTiles(url, callback) {
    const img = new Image();
    img.onload = function() {callback(true);};
    img.onerror = function() {callback(false);};
    img.src = url.replace('{z}', 0).replace('{x}', 0).replace('{y}', 0);
}

// URLs for local and remote tiles
let localTileUrl = 'http://localhost:5000/data/tiles/{z}/{x}/{y}.png';
let remoteTileUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';

// Check if local tiles are available
checkLocalTiles(localTileUrl, function(isLocalAvailable) {
    const tileUrl = isLocalAvailable ? localTileUrl : remoteTileUrl;
    //const tileUrl = localTileUrl;
    L.tileLayer(tileUrl, {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
});


L.control.locate({ drawCircle: false }).addTo(map);


const markers = L.markerClusterGroup();
fetch('/api/wifi_pass_map')
  .then(response => response.json())
  .then(result => {
    console.log('Result:', result);
    const {data, script_statuses, AP_len} = result;

    const script_success = script_statuses.filter(script => script.status === 'success').length;
    const script_count_all = script_statuses.length;

    createStatsDiv(script_success, script_count_all, AP_len, script_statuses);

    // Create a marker cluster group

    data.forEach(poi => {
      const marker = createMarker(poi);
      markers.addLayer(marker);
    });

    map.addLayer(markers);

  })
  .catch(error => console.error("Error fetching data:", error));


function searchAndRefreshMap() {
    // Clear existing markers
    markers.clearLayers();

    const networkType = document.getElementById('networkType').value;
    const encryption = document.getElementById('encryption').value;
    const searchQueryName = document.getElementById('searchInputName').value.trim();
    const searchQueryNetworkId = document.getElementById('searchInputNetworkId').value.trim();
    const searchInputLimit = document.getElementById('searchInputLimit').value.trim();
    //const excludeNoSSID = document.getElementById('excludeNoSSID').checked;

    let url = '/api/explore';
    const filters = [];

    if (networkType) filters.push('network_type=' + networkType);
    if (encryption) filters.push('encryption=' + encryption);
    if (searchQueryName) filters.push('name=' + encodeURIComponent(searchQueryName));
    if (searchQueryNetworkId) filters.push('network_id=' + encodeURIComponent(searchQueryNetworkId));
    if (searchInputLimit) filters.push('limit=' + encodeURIComponent(searchInputLimit));
    //TODO ignore fot now
    // if (excludeNoSSID) filters.push('exclude_no_ssid=true');
    if (filters.length > 0) url += '?' + filters.join('&');

    // Fetch data from API
    fetch(url)
    .then(response => response.json())
    .then(result => {
        //console.log('Result:', result);
        const {data, script_statuses, AP_len} = result;

        const script_success = script_statuses.filter(script => script.status === 'success').length;
        const script_count_all = script_statuses.length;

        const statsDiv = document.getElementById('stats-popup');
        statsDiv.remove();
        createStatsDiv(script_success, script_count_all, AP_len, script_statuses);

        // Create a marker cluster group

        data.forEach(poi => {
            const marker = createMarker(poi);
            markers.addLayer(marker);
        });

        map.addLayer(markers);
    })
    .catch(error => console.error('Error fetching data:', error));
}

//when search and refresh map?
document.getElementById('searchInputName').addEventListener('keypress', event => {
    if (event.key === 'Enter') searchAndRefreshMap();
});
document.getElementById('searchInputNetworkId').addEventListener('keypress', event => {
    if (event.key === 'Enter') searchAndRefreshMap();
});
document.getElementById('searchButton').addEventListener('click', searchAndRefreshMap);

map.on('click', function(event) {
    const latitude = event.latlng.lat;
    const longitude = event.latlng.lng;

    document.getElementById('center_lat').value = latitude;
    document.getElementById('center_long').value = longitude;
});

document.getElementById('loadButton').addEventListener('click', function() {
    const latitude = document.getElementById('center_lat').value;
    const longitude = document.getElementById('center_long').value;

    let url = '/api/load_sqare';
    const filters = [];

    const networkType = document.getElementById('networkType').value;
    if (networkType) filters.push('network_type=' + networkType);
    filters.push('center_latitude=' + latitude);
    filters.push('center_longitude=' + longitude);

    const searchInputCenterLimit = document.getElementById('searchInputCenterLimit').value.trim();
    if (searchInputCenterLimit) filters.push('center_limit=' + encodeURIComponent(searchInputCenterLimit));

    if (filters.length > 0) url += '?' + filters.join('&');

    fetch(url)
        .then(response => response.json())
        .then(result => {
            //TODO add, not replace
            markers.clearLayers();

            const {data, script_statuses, AP_len} = result;
            // Process the result as needed

            const script_success = script_statuses.filter(script => script.status === 'success').length;
            const script_count_all = script_statuses.length;

            const statsDiv = document.getElementById('stats-popup');
            statsDiv.remove();
            createStatsDiv(script_success, script_count_all, AP_len, script_statuses);

            // Create a marker cluster group

            data.forEach(poi => {
                const marker = createMarker(poi);
                markers.addLayer(marker);
            });

            map.addLayer(markers);

        })
        .catch(error => console.error('Error fetching data:', error));
});