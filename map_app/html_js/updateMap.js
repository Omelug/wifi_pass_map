var circles = [];
var maxRadius = 20;

function updateMap() {
    var zoomLevel = {map_var}.getZoom();
    var bounds = {map_var}.getBounds();
    var bbox = [bounds.getSouthWest().lat, bounds.getSouthWest().lng, bounds.getNorthEast().lat, bounds.getNorthEast().lng];
    console.log(`Updating {map_var}... ${zoomLevel}`);
    var url = `/update_map?zoom=${zoomLevel}&bbox=${bbox.join(',')}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            // Remove old circles
            circles.forEach(circle => {map_var}.removeLayer(circle));
            circles = [];

            var dynamicPane = {map_var}.getPane('dynamic_pane');
            dynamicPane.innerHTML = '';

            data.forEach(function(point) {

                var radius = Math.max(10, Math.min(2 + Math.sqrt(point.count) * 2, maxRadius));
                var color = point.count > 1 ? 'red' : 'purple';
                var AP_info = `ESSID: ${point.ESSID}<br>WifiKey: ${point.WifiKey}`;
                var popupText = (point.count > 1 && zoomLevel < 18) ? `${point.count} APs` : AP_info;
                console.log(data);

                var circle = L.circleMarker([point.latitude, point.longitude], {
                    radius: radius,
                    color: color,
                    fillColor: color,
                    fillOpacity: 0.6
                }).bindPopup(popupText).addTo({map_var});

                circle.on('click', function() {
                    document.getElementById('info-panel').innerHTML = AP_info;
                });

                circles.push(circle);
            });
        });
}
document.getElementById('update-button').addEventListener('click', function() {
    updateMap();
});
{map_var}.on('zoomend', updateMap);
//{map_var}.on('moveend', updateMap);
updateMap();