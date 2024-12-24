function generateGeoSchemeURL(latitude, longitude) {
  return `geo:${latitude},${longitude}`;
}

function generateWifiUriScheme(ssid, encryption, password) {
  return `WIFI:S:${ssid};T:${encryption};P:${password};H:false;`;
}

function createQRCode(data) {
  var qr = qrcode(0, 'M'); // Error correction level
  qr.addData(data);
  qr.make();
  return qr.createDataURL(10, 0); // Size,margin
}

function generateQrCode(wifiUri) {
  window.open(createQRCode(wifiUri), '_blank');
}

var map = L.map('map').setView([0, 0], 2);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors',
  maxZoom: 24
}).addTo(map);

L.control.locate({ drawCircle: false }).addTo(map);

fetch('/api/wifi_pass_map')
  .then((response) => response.json())
  .then((result) => {
    console.log('Result:');
      const { data, script_statuses, AP_len } = result;
    //console.log('Data:', data);
    // Count successful scripts
    const script_success = script_statuses.filter(script => script.status === 'success').length;
    const script_count_all = script_statuses.length;

    // Create the stats div
    const statsDiv = document.createElement('div');
    statsDiv.id = 'stats-popup';
    statsDiv.style.position = 'fixed';
    statsDiv.style.top = '10px';
    statsDiv.style.right = '10px';
    statsDiv.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
    statsDiv.style.color = 'white';
    statsDiv.style.padding = '10px';
    statsDiv.style.borderRadius = '5px';
    statsDiv.style.zIndex = '1000';

    // Add the main stats
    statsDiv.innerHTML = `Scripts: ${script_success}/${script_count_all} APs: ${AP_len}<br>`;

    // Add the script statuses
    script_statuses.forEach(script => {
      const scriptDiv = document.createElement('div');
      scriptDiv.textContent = script.name;
      scriptDiv.style.color = script.status === 'success' ? 'green' : (script.status === 'empty' ? 'orange' : 'red');
      statsDiv.appendChild(scriptDiv);
    });

    // Append the stats div to the body
    document.body.appendChild(statsDiv);

    let totalLat = 0;
    let totalLng = 0;
    let count = data.length;

    data.forEach((poi) => {
      totalLat += poi.latitude;
      totalLng += poi.longitude;
    });

    let avgLat = totalLat / count || 0;
    let avgLng = totalLng / count || 0;

    if (avgLat && avgLng) {
      map.setView([avgLat, avgLng], 10);
    }

    data.forEach((poi) => {
      var radius = poi.accuracy ?? 0;

      var geoSchemeURL = generateGeoSchemeURL(poi.latitude, poi.longitude);
      poi.wifiUri = generateWifiUriScheme(poi.name, poi.encryption, poi.password);

      var circle = L.circle([poi.latitude, poi.longitude], {
        radius: radius,
        color: '#fc0865',
        weight: 2,
        fill: false,
      });

      var marker = L.marker([poi.latitude, poi.longitude]);

      var popupContent = `
        <strong>Name:</strong> ${poi.name}<br>
        <strong>Password:</strong> ${poi.password}<br>
        <strong>Accuracy:</strong> ${poi.accuracy} meters<br>
        <button onclick="window.open('${geoSchemeURL}', '_blank')">Navigate to</button><button onclick="generateQrCode('${poi.wifiUri}')">Show QR</button><br>
        
      `;

      marker.addTo(map).bindPopup(popupContent);

      marker.on("click", function() {
        map.setView([poi.latitude, poi.longitude], 19); // Center and zoom in on click
        map.addLayer(circle); // Add circle when the marker is clicked
      });

      marker.on("popupclose", function() {
        map.removeLayer(circle); // popup is closed -> Remove circle
      });
    });
  })
  .catch((error) => console.error("Error fetching data:", error));
