import datetime
import temperature

def air_temperature(data: dict, scale: str, length: int, limit: str) -> str:
    """
    Given a dictionary with forecast data, a temperature scale ('C' or 'F'), the number of hours to search, and 'MAX' or
    'MIN' depending on which is desired, finds the maximum or minimum air temperature in that time period.
    """
    target_temp = None
    target_datetime = None

    periods = data['properties']['periods']
    for i in range(length):
        curr_datetime = periods[i]['startTime']

        curr_temp = periods[i]['temperature']

        if scale == 'C':
            curr_temp = temperature.celsius(curr_temp)

        target_temp, target_datetime = _process_curr_item(curr_temp, target_temp, curr_datetime, target_datetime, limit)

    return f'{_datetime_to_utc(target_datetime)} {target_temp:.4f}'


def feels_like_temperature(data: dict, scale: str, length: int, limit: str) -> str:
    """
    Given a dictionary with forecast data, a temperature scale ('C' or 'F'), the number of hours to search, and 'MAX' or
    'MIN' depending on which is desired, finds the maximum or minimum 'feels like' temperature in that time period. If
    the temperature is above 68 degrees F, this temperature is calculated by the heat index. If the temperature is
    below 50 degrees F and the wind speed is above 3 mph, it is instead calculated by the wind chill.
    """
    target_temp = None
    target_datetime = None

    periods = data['properties']['periods']
    for i in range(length):
        curr_datetime = periods[i]['startTime']

        curr_temp = periods[i]['temperature']
        curr_humidity = periods[i]['relativeHumidity']['value']
        curr_wind = _simplify_wind_speed(periods[i]['windSpeed'])

        if curr_temp >= 68:
            curr_temp = temperature.calc_heat_index(curr_temp, curr_humidity)
        elif curr_temp <= 50 and curr_wind > 3:
            curr_temp = temperature.calc_wind_chill(curr_temp, curr_wind)

        if scale == 'C':
            curr_temp = temperature.celsius(curr_temp)

        target_temp, target_datetime = _process_curr_item(curr_temp, target_temp, curr_datetime, target_datetime, limit)

    return f'{_datetime_to_utc(target_datetime)} {target_temp:.4f}'


def humidity(data: dict, length: int, limit: str) -> str:
    """
    Given a dictionary with forecast data, the number of hours to search, and 'MAX' or 'MIN' depending on which is
    desired, finds the maximum or minimum air humidity in that time period.
    """
    target_humidity = None
    target_datetime = None

    periods = data['properties']['periods']
    for i in range(length):
        curr_datetime = periods[i]['startTime']

        curr_humidity = periods[i]['relativeHumidity']['value']

        target_humidity, target_datetime = _process_curr_item(curr_humidity, target_humidity, curr_datetime, target_datetime, limit)

    return f'{_datetime_to_utc(target_datetime)} {target_humidity:.4f}%'


def wind_speed(data: dict, length: int, limit: str) -> str:
    """
    Given a dictionary with forecast data, the number of hours to search, and 'MAX' or 'MIN' depending on which is
    desired, finds the maximum or minimum air wind speed in that time period.
    """
    target_wind = None
    target_datetime = None

    periods = data['properties']['periods']
    for i in range(length):
        curr_datetime = periods[i]['startTime']

        curr_wind = _simplify_wind_speed(periods[i]['windSpeed'])

        target_wind, target_datetime = _process_curr_item(curr_wind, target_wind, curr_datetime, target_datetime, limit)

    return f'{_datetime_to_utc(target_datetime)} {target_wind:.4f}'


def chance_of_precipitation(data: dict, length: int, limit: str) -> str:
    """
    Given a dictionary with forecast data, the number of hours to search, and 'MAX' or 'MIN' depending on which is
    desired, finds the maximum or minimum air chance of precipitation in that time period.
    """
    target_rain_chance = None
    target_datetime = None

    periods = data['properties']['periods']
    for i in range(length):
        curr_datetime = periods[i]['startTime']

        curr_rain_chance = periods[i]['probabilityOfPrecipitation']['value']

        target_rain_chance, target_datetime = _process_curr_item(curr_rain_chance, target_rain_chance, curr_datetime, target_datetime, limit)

    return f'{_datetime_to_utc(target_datetime)} {target_rain_chance:.4f}%'


def get_latitude_and_longitude(geocoding_data: dict) -> tuple[float, float]:
    """
    Given a dictionary with forward geocoding data, returns the latitude and longitude of the location.
    """
    latitude = geocoding_data[0]['lat']
    longitude = geocoding_data[0]['lon']

    return float(latitude), float(longitude)


def determine_forecast_location(forecast_data: dict) -> tuple[float, float]:
    """
    Given a dictionary with NWS forecast data, finds the points of a polygon bounding the forecast location and takes
    the average of the latitudes/longitudes to calculate the location of a point directly in the middle of the polygon.
    Returns the latitude and longitude of this point.
    """
    polygon_coords = forecast_data['geometry']['coordinates'][0]
    unique_coords = set()

    for coordinate in polygon_coords:
        unique_coords.add(tuple(coordinate))

    lat_sum = 0
    lon_sum = 0
    for coordinate in unique_coords:
        lon_sum += coordinate[0]
        lat_sum += coordinate[1]

    avg_lat = lat_sum / len(unique_coords)
    avg_lon = lon_sum / len(unique_coords)

    return avg_lat, avg_lon


def get_forecast_location_address(rev_geocoding_data: dict) -> str:
    """
    Given a dictionary with reverse geocoding data, returns the full address name of the location.
    """
    address = rev_geocoding_data['display_name']
    return address


def _simplify_wind_speed(wind_speed_data: str) -> float:
    """
    Given a string containing the wind speed (formatted as '# mph'), strips off unnecessary text and returns the wind
    speed as a float.
    """
    speed = wind_speed_data.split(' ')[0]
    return float(speed)


def _process_curr_item(curr: float, target: float, curr_datetime: str, target_datetime: str, limit: str) -> tuple[float, str]:
    """
    Compares two items in the data set, and returns the largest or smallest (depending on what 'limit' stores), along
    with its datetime.
    """
    if (target == None) or (limit == 'MAX' and curr > target) or (limit == 'MIN' and curr < target):
        return curr, curr_datetime
    else:
        return target, target_datetime


def _datetime_to_utc(date_and_time: str) -> str:
    """
    Given the datetime string in ISO 8601 format, converts it to the UTC timezone.
    """
    datetime_obj = datetime.datetime.fromisoformat(date_and_time)

    return datetime_obj.astimezone(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')