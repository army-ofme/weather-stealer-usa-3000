import forward_geocoding
import reverse_geocoding
import weather_forecast
import data_processing

def run_weather_ui() -> None:
    """
    Runs the main UI. Receives the user's input, fetches all necessary data, calculates results of each query, and outputs
    all the results.
    """
    target_type, weather_type, weather_queries, reverse_type = _get_query_input()

    fwd_geocoding_obj, fwd_geocoding_api_used = _process_target_choice(target_type)
    fwd_geocoding_data = fwd_geocoding_obj.fetch_data()
    if fwd_geocoding_data is None:
        return
    target_location = data_processing.get_latitude_and_longitude(fwd_geocoding_data)

    forecast_data_obj, weather_api_used = _process_weather_choice(weather_type, target_location)
    forecast_data = forecast_data_obj.fetch_data()
    if forecast_data is None:
        return
    forecast_location = data_processing.determine_forecast_location(forecast_data)

    rev_geocoding_obj, rev_geocoding_api_used = _process_reverse_choice(reverse_type, forecast_location)
    rev_geocoding_data = rev_geocoding_obj.fetch_data()
    if rev_geocoding_data is None:
        return
    forecast_location_address = data_processing.get_forecast_location_address(rev_geocoding_data)

    query_results = _get_query_results(weather_queries, forecast_data)
    _print_output(query_results, target_location, forecast_location, forecast_location_address)
    _print_attributions(fwd_geocoding_api_used, weather_api_used, rev_geocoding_api_used)


def _get_query_input() -> tuple[str, str, list[str], str]:
    """
    Prompts user for input for where they want the data to come from (API or file) for each data category, as well as
    any queries they make, until 'NO MORE QUERIES' is received. Returns the choice for each category, as well as the
    list of queries.
    """
    target = input()
    weather = input()

    weather_queries = []
    while True:
        query = input()

        if query == 'NO MORE QUERIES':
            break
        else:
            weather_queries.append(query)

    reverse = input()
    print()

    return target, weather, weather_queries, reverse


def _process_target_choice(target_input: str) -> tuple[
    forward_geocoding.ForwardGeocodingAPI, bool] | tuple[forward_geocoding.ForwardGeocodingFile, bool]:
    """
    Given the input pertaining to forward geocoding data, returns either a corresponding API or File object, as well as
    a boolean (True if API was used, False otherwise).
    """
    args = target_input.split(' ', maxsplit = 2)
    if args[1] == 'NOMINATIM':
        return forward_geocoding.ForwardGeocodingAPI(args[2]), True
    elif args[1] == 'FILE':
        return forward_geocoding.ForwardGeocodingFile(args[2]), False


def _process_weather_choice(weather_input: str, target_location: tuple[float, float]) -> tuple[
    weather_forecast.WeatherForecastAPI, bool] | tuple[weather_forecast.WeatherForecastFile, bool]:
    """
    Given the input pertaining to weather data, returns either a corresponding API or File object, as well as a boolean
    (True if API was used, False otherwise).
    """
    args = weather_input.split(' ')
    if args[1] == 'NWS':
        latitude, longitude = target_location
        return weather_forecast.WeatherForecastAPI(latitude, longitude), True
    elif args[1] == 'FILE':
        return weather_forecast.WeatherForecastFile(args[2]), False


def _process_reverse_choice(reverse_input: str, forecast_location: tuple[float, float]) -> tuple[
    reverse_geocoding.ReverseGeocodingAPI, bool] | tuple[reverse_geocoding.ReverseGeocodingFile, bool]:
    """
    Given the input pertaining to reverse geocoding data, returns either a corresponding API or File object, as well as
    a boolean (True if API was used, False otherwise).
    """
    args = reverse_input.split(' ')
    if args[1] == 'NOMINATIM':
        latitude, longitude = forecast_location
        return reverse_geocoding.ReverseGeocodingAPI(latitude, longitude), True
    elif args[1] == 'FILE':
        return reverse_geocoding.ReverseGeocodingFile(args[2]), False


def _get_query_results(queries: list[str], forecast_data: dict) -> list[str]:
    """
    Given the list of provided queries and the dictionary containing forecast data, goes through the list and performs
    each query. If the NWS API returns fewer hours than the user asks for, the query will simply use as many hours as
    were given. Adds the results of each query to a list and returns the list.
    """
    query_results = []

    for query in queries:
        args = query.split(' ')

        if args[0] == 'TEMPERATURE':
            query_type, scale, length, limit = args[1], args[2], int(args[3]), args[4]
            length = min(length, _available_num_of_time_periods(forecast_data))

            if query_type == 'AIR':
                query_results.append(data_processing.air_temperature(forecast_data, scale, length, limit))
            elif query_type == 'FEELS':
                query_results.append(data_processing.feels_like_temperature(forecast_data, scale, length, limit))
        else:
            query_type, length, limit = args[0], int(args[1]), args[2]
            length = min(length, _available_num_of_time_periods(forecast_data))

            if query_type == 'HUMIDITY':
                query_results.append(data_processing.humidity(forecast_data, length, limit))
            elif query_type == 'WIND':
                query_results.append(data_processing.wind_speed(forecast_data, length, limit))
            elif query_type == 'PRECIPITATION':
                query_results.append(data_processing.chance_of_precipitation(forecast_data, length, limit))

    return query_results


def _available_num_of_time_periods(forecast_data: dict) -> int:
    """
    Given a dictionary with forecast data, returns how many time periods of data were sent.
    """
    return len(forecast_data['properties']['periods'])


def _print_output(query_results: list[str], target_loc: tuple[float, float], forecast_loc: tuple[float, float], forecast_addr: str) -> None:
    """
    Given the weather query results, the target location, forecast location, and address for the forecast location,
    prints each one of these items.
    """
    target_lat, target_lon = _convert_coords_to_strings(target_loc)
    forecast_lat, forecast_lon = _convert_coords_to_strings(forecast_loc)

    print(f'TARGET {target_lat} {target_lon}')
    print(f'FORECAST {forecast_lat} {forecast_lon}')
    print(f'{forecast_addr}')


    for result in query_results:
        print(result)


def _convert_coords_to_strings(coords: tuple[float, float]) -> tuple[str, str]:
    """
    Given a 2-tuple of floats representing latitude and longitude, converts them from a numeric expression (-23, 32) to
    a string representation (23/S 32/E)
    """
    if coords[0] < 0:
        latitude = coords[0] * -1
        lat_direction = 'S'
    else:
        latitude = coords[0]
        lat_direction = 'N'

    if coords[1] < 0:
        longitude = coords[1] * -1
        lon_direction = 'W'
    else:
        longitude = coords[1]
        lon_direction = 'E'

    return f'{latitude}/{lat_direction}', f'{longitude}/{lon_direction}'


def _print_attributions(fwd_geo_used: bool, weather_api_used: bool, rev_geo_used: bool) -> None:
    """
    If any of the three API requests were made, prints an attribution to where that data came from.
    """
    print()

    if fwd_geo_used:
        print('**Forward geocoding data from OpenStreetMap')
    if rev_geo_used:
        print('**Reverse geocoding data from OpenStreetMap')
    if weather_api_used:
        print('**Real-time weather data from National Weather Service, United States Department of Commerce')


if __name__ == '__main__':
    run_weather_ui()