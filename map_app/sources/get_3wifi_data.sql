SELECT nets.BSSID, ESSID, WifiKey, latitude,longitude
        FROM nets
        JOIN geo ON nets.BSSID = geo.BSSID
        WHERE latitude BETWEEN 48.474378 AND 51.045193
        AND longitude BETWEEN 12.068481 AND 18.860779
        LIMIT 1000;