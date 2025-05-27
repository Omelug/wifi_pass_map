import logging
from app.tools.db import get_db_connection

def populate_pwned_data():
    new_networks = 0  # Counter for new networks with geolocation
    no_geolocation_networks = 0  # Counter for networks with no geolocation
    total_networks = 0 # Counter for total processed Networks

    # Connect to SQLite database
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Query wpasec table
        cursor.execute('SELECT bssid, password FROM wpasec')
        wpasec_data = cursor.fetchall()

        # Query wigle table and populate pwned table
        for row in wpasec_data:
            ap_mac = row[0]
            password = row[1]

            total_networks += 1 # Counter for total proccessed Networks

            # Convert bssid to the format used in the wigle table
            # Query wigle table for the corresponding network_id (case-insensitive matching)
            cursor.execute('SELECT name, network_id, encryption, accuracy, latitude, longitude FROM wigle WHERE lower(network_id) = lower(?)', (bssid,))
            wigle_data = cursor.fetchone()

            # If data is found in the wigle table, insert into pwned table
            if wigle_data:
                name, network_id, encryption, accuracy, latitude, longitude = wigle_data
                # Check if the name already exists in pwned table (to avoid duplicates based on 'name')
                cursor.execute('SELECT name FROM pwned WHERE name = ?', (name,))
                existing_record = cursor.fetchone()
                if not existing_record:
                    new_networks += 1
                    cursor.execute('''
                        INSERT INTO pwned (name, network_id, encryption, accuracy, latitude, longitude, password)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (name, network_id, encryption, accuracy, latitude, longitude, password))
            else:
                no_geolocation_networks += 1

    except Exception as e:
        logging.error("An error occurred:", str(e))
    finally:
        # Commit changes and close the connection
        conn.commit()
        conn.close()

    return new_networks, no_geolocation_networks, total_networks



