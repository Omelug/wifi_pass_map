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

  const circle = L.circle([poi.latitude, poi.longitude], {
    radius: 2000,
    color: '#fc0865',
    weight: 2,
    fill: false,
  });

  const marker = L.marker([poi.latitude, poi.longitude]);

  const popupContent = `
    <strong>bssid:</strong> ${poi.bssid}<br>
    <strong>essid:</strong> ${poi.essid}<br>
    <strong>encryption:</strong> ${poi.encryption}<br>
    <strong>password:</strong> ${poi.password}<br>
    <button onclick="window.open('${geoSchemeURL}', '_blank')">Navigate to</button>
    <button onclick="generateQrCode('${poi.wifiUri}')">Show QR</button><br>  
  `;

  marker.addTo(map).bindPopup(popupContent);

  marker.on("click", function() { map.addLayer(circle); });
  marker.on("popupclose", function() { map.removeLayer(circle); });
}

//TODo hardcoded to czech republic
const map = L.map('map').setView([49.8175, 15.4730], 7);

//TODO create possibility to get data from openstreetmap data on local
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: 'OpenStreetMap contributors',
  maxZoom: 24
}).addTo(map);

L.control.locate({ drawCircle: false }).addTo(map);

fetch('/api/wifi_pass_map')
  .then(response => response.json())
  .then(result => {
    console.log('Result:', result);
    const { data, script_statuses, AP_len } = result;

    const script_success = script_statuses.filter(script => script.status === 'success').length;
    const script_count_all = script_statuses.length;

    createStatsDiv(script_success, script_count_all, AP_len, script_statuses);

    data.forEach(createMarker);
  })
  .catch(error => console.error("Error fetching data:", error));
