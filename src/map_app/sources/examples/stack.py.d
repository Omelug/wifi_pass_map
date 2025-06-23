@staticmethod
def __load_random_APs_to_limit(filters=None):
    with open('map_app/sources/get_3wifi_data.sql', 'r') as file:
        sql_script = file.read()
    limit = 10000000
    if filters:
        filter_conditions = ""
        if 'limit' in filters:
            limit = filters.pop('limit')
        sql_script = sql_script[:-1]
        if not filters:
            sql_script += f" LIMIT {limit};"
        else:
            # Remove the trailing semicolon
            if 'bssid' in filters:
                filter_conditions += f"nets.BSSID = {mac2dec(filters.pop('bssid'))} "
            filter_conditions += " AND ".join([f"{key} = :{key}" for key in filters.keys()])
            sql_script += f" AND {filter_conditions} LIMIT {limit};"
    else:
        return f"{sql_script[:-1]} LIMIT {limit};"
    return sql_script


@staticmethod
def __load_map_square(center_latitude, center_longitude, center_limit=0.05):
    logging.info(center_latitude, center_longitude, center_limit)
    logging.info("\n\n")
    sql_query = f"""
        SELECT nets.BSSID, ESSID, WifiKey, geo.latitude, geo.longitude
        FROM nets
        JOIN geo ON nets.BSSID = geo.BSSID
        WHERE geo.latitude BETWEEN {center_latitude} - {center_limit} AND {center_latitude} + {center_limit}
          AND geo.longitude BETWEEN {center_longitude} - {center_limit} AND {center_longitude} + {center_limit}
        LIMIT 10000000;
    """
    return sql_query

  def get_map_data(self, filters=None):
        try:
            with self._get_db_connection() as connection:
                if filters and 'center_latitude' in filters and 'center_longitude' in filters:
                    sql_script = self.__load_map_square(
                        filters['center_latitude'],
                        filters['center_longitude'],
                        filters.get('center_limit', 0.05)
                    )
                else:
                    sql_script = self.__load_random_APs_to_limit(filters)

                rows = connection.execute(text(sql_script), filters).fetchall()

        except exc.SQLAlchemyError as e:
            logging.error(f"An error occurred: {e}")
            return []

        return [
            {
                "bssid": dec2mac(row[0]),
                "essid": row[1],
                "password": row[2],
                "latitude": row[3],
                "longitude": row[4]
            }
            for row in rows
        ]

