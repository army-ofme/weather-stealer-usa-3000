import json
from pathlib import Path
import urllib.error
import urllib.request

NWS_URL = 'https://api.weather.gov'

class WeatherForecastAPI:
    """
    Class to fetch weather forecast data from NWS (National Weather Service), given a latitude and longitude.
    """
    def __init__(self, latitude: float, longitude: float):
        self._url = f'{NWS_URL}/points/{latitude},{longitude}'
        self._headers = {
            'User-Agent': '(https://www.ics.uci.edu/~thornton/icsh32/ProjectGuide/Project3/, ecbaker@uci.edu)',
            'Accept': 'application/geo+json'
        }


    def fetch_data(self) -> dict | None:
        """
        Sends an initial API request to NWS with the desired latitude, longitude and headers, stores the response as
        dictionary in JSON format, then grabs the URL for the second API request. This URL is used to request the
        forecast data. This data is received and returned as a dictionary in JSON format. Returns None in the case of
        API failure.
        """
        http_code = ''
        metadata_response = None
        forecast_response = None

        try:
            metadata_request = urllib.request.Request(
                url = self._url,
                headers = self._headers
            )
            metadata_response = urllib.request.urlopen(metadata_request)
            http_code = metadata_response.getcode()
            if http_code != 200:
                raise urllib.error.HTTPError
            metadata = metadata_response.read().decode(encoding = 'utf-8')
            metadata = json.loads(metadata)

            forecast_url = metadata['properties']['forecastHourly']
            forecast_request = urllib.request.Request(
                url = forecast_url,
                headers = self._headers
            )
            forecast_response = urllib.request.urlopen(forecast_request)
            http_code = forecast_response.getcode()
            if http_code != 200:
                raise urllib.error.HTTPError
            forecast = forecast_response.read().decode(encoding = 'utf-8')
            return json.loads(forecast)
        except urllib.error.HTTPError:
            _print_error(f'{http_code} {self._url}', 'NOT 200')
            return None
        except json.JSONDecodeError:
            _print_error(f'{http_code} {self._url}', 'FORMAT')
            return None
        except urllib.error.URLError:
            _print_error(f'{http_code} {self._url}', 'NETWORK')
            return None
        finally:
            if metadata_response != None:
                metadata_response.close()
            if forecast_response != None:
                forecast_response.close()


class WeatherForecastFile:
    """
    Class to fetch weather forecast data from a locally stored file.
    """
    def __init__(self, path: str):
        self._path = Path(path)


    def fetch_data(self) -> dict | None:
        """
        Attempts to open a given JSON file with weather forecast data and returns the data as a dictionary. Returns None
        if the file could not be accessed or if it is in the wrong format.
        """
        weather_data = None

        try:
            weather_data = self._path.open('r')

            return json.load(weather_data)
        except OSError:
            _print_error(str(self._path.absolute()), 'MISSING')
            return None
        except json.JSONDecodeError:
            _print_error(str(self._path.absolute()), 'FORMAT')
            return None
        finally:
            if weather_data != None:
                weather_data.close()


def _print_error(first_arg: str, second_arg: str) -> None:
    """
    Prints the cause for error if an exception is raised.
    """
    print('FAILED')
    print(first_arg.strip())
    print(second_arg)