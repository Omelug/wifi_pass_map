let circles = [];
let maxRadius = 20;

function updateMap() {
    const zoomLevel = map_var.getZoom();
    const bounds = map_var.getBounds();
    const bbox = [bounds.getSouthWest().lat, bounds.getSouthWest().lng, bounds.getNorthEast().lat, bounds.getNorthEast().lng];
    console.log(`Updating map... ${zoomLevel}`);
    const url = `/update_map?zoom=${zoomLevel}&bbox=${bbox.join(',')}`;

   fetch(url)
        .then(response => response.json())
        .then(data => {
            // Remove old circles
            circles.forEach(circle => map_var.removeLayer(circle));
            circles = [];

            const dynamicPane = map_var.getPane('dynamic_pane');
            dynamicPane.innerHTML = '';

            data.forEach(function(point) {
                const radius = Math.max(10, Math.min(2 + Math.sqrt(point.count) * 2, maxRadius));
                const color = point.count > 1 ? 'red' : 'purple';
                const AP_info = `ESSID: ${point.ESSID}<br>WifiKey: ${point.WifiKey}`;
                const popupText = (point.count > 1 && zoomLevel < 18) ? `${point.count} APs` : AP_info;
                console.log(data);

                const circle = L.circleMarker([point.latitude, point.longitude], {
                    radius: radius,
                    color: color,
                    fillColor: color,
                    fillOpacity: 0.6
                }).bindPopup(popupText).addTo(map_var);

                circle.on('click', function() {
                    document.getElementById('info-panel').innerHTML = AP_info;
                });

                circles.push(circle);
            });
        });
}
/*document.getElementById('update-button').addEventListener('click', function() {
    updateMap();
});*/
//{map_var}.on('zoomend', updateMap);
//{map_var}.on('moveend', updateMap);
//updateMap();