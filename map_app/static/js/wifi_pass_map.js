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
  statsDiv.innerHTML = `Scripts: ${script_success}/${script_count_all} APs: ${AP_len}<br>`;

  script_statuses.forEach(script => {
    const scriptDiv = document.createElement('div');
    scriptDiv.textContent = script.name;
    scriptDiv.style.color = script.status === 'success' ? 'green' : (script.status === 'empty' ? 'orange' : 'red');
    statsDiv.appendChild(scriptDiv);
  });

  document.body.appendChild(statsDiv);
}

function createMarker(poi) {
  const geoSchemeURL = generateGeoSchemeURL(poi.latitude, poi.longitude);
  poi.wifiUri = generateWifiUriScheme(poi.essid, poi.encryption, poi.password);

  /*const circle = L.circle([poi.latitude, poi.longitude], {
    radius: 2000,
    color: '#fc0865',
    weight: 2,
    fill: false,
  });*/

  const popupContent = `
    <strong>bssid:</strong> ${poi.bssid}<br>
    <strong>essid:</strong> ${poi.essid}<br>
    <strong>encryption:</strong> ${poi.encryption}<br>
    <strong>password:</strong> ${poi.password}<br>
    <button onclick="window.open('${geoSchemeURL}', '_blank')">Navigate to</button>
    <button onclick="generateQrCode('${poi.wifiUri}')">Show QR</button><br>  
  `;

  let marker = L.marker([poi.latitude, poi.longitude]).bindPopup(popupContent);


  //marker.on("click", function() { map.addLayer(circle); });
  //marker.on("popupclose", function() { map.removeLayer(circle); });
  return marker;
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
let localTileUrl = 'http://localhost:5000/tiles/{z}/{x}/{y}.png';
let remoteTileUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';

// Check if local tiles are available
checkLocalTiles(localTileUrl, function(isLocalAvailable) {
    const tileUrl = isLocalAvailable ? localTileUrl : remoteTileUrl;
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
    const excludeNoSSID = document.getElementById('excludeNoSSID').checked;

    let url = '/api/explore';
    const filters = [];

    if (networkType) filters.push('network_type=' + networkType);
    if (encryption) filters.push('encryption=' + encryption);
    if (searchQueryName) filters.push('name=' + encodeURIComponent(searchQueryName));
    if (searchQueryNetworkId) filters.push('network_id=' + encodeURIComponent(searchQueryNetworkId));
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


