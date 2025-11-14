def celsius(temp_in_fahr: float) -> float:
    """
    Given the temperature in Fahrenheit, converts to Celsius.
    """
    return (temp_in_fahr - 32) * (5 / 9)


def fahrenheit(temp_in_cels: float) -> float:
    """
    Given the temperature in Celsius, converts to Fahrenheit.
    """
    return (temp_in_cels * (9 / 5)) + 32


def calc_heat_index(t: float, h: float) -> float:
    """
    Given the temperature in Fahrenheit and the humidity (as a percent), calculates the heat index.
    """
    heat_index_parts = [
        -42.379,
        2.04901523 * t,
        10.14333127 * h,
        -0.22475541 * t * h,
        -0.00683783 * t * t,
        -0.05481717 * h * h,
        0.00122874 * t * t * h,
        0.00085282 * t * h * h,
        -0.00000199 * t * t * h * h
    ]

    heat_index = 0
    for arg in heat_index_parts:
        heat_index += arg

    return heat_index


def calc_wind_chill(t: float, w: float) -> float:
    """
    Given the temperature in Fahrenheit and the wind speed in miles per hour, calculates the wind chill.
    """
    wind_chill_parts = [
        35.74,
        0.6215 * t,
        -35.75 * (w ** 0.16),
        0.4275 * t * (w ** 0.16)
    ]

    wind_chill = 0
    for arg in wind_chill_parts:
        wind_chill += arg

    return wind_chill