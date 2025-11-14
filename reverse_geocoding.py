import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

NOMINATIM_URL = 'https://nominatim.openstreetmap.org'

class ReverseGeocodingAPI:
    """
    Class to fetch reverse geocoding data from Nominatim, given a latitude and longitude.
    """
    def __init__(self, latitude: float, longitude: float):
        self._latitude = latitude
        self._longitude = longitude
        self._url = self._build_search_url()
        self._headers = { 'Referer': 'https://www.ics.uci.edu/~thornton/icsh32/ProjectGuide/Project3/ecbaker' }


    def fetch_data(self) -> dict | None:
        """
        Sends an API request to Nominatim with the search URL and proper header, then receives the API's response and
        returns the reverse geocoding data as a dictionary in JSON format. Returns None in the case of API failure.
        """
        http_code = ''
        response = None

        try:
            request = urllib.request.Request(
                url = self._url,
                headers = self._headers
            )
            response = urllib.request.urlopen(request)
            http_code = response.getcode()
            if http_code != 200:
                raise urllib.error.HTTPError
            location_data = response.read().decode(encoding = 'utf-8')

            return json.loads(location_data)
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
            if response != None:
                response.close()


    def _build_search_url(self) -> str:
        """
        Returns an encoded search URL for the Nominatim API reverse search request.
        """
        query_params = [
            ('lat', self._latitude), ('lon', self._longitude), ('format', 'jsonv2')
        ]
        return f'{NOMINATIM_URL}/reverse?{urllib.parse.urlencode(query_params)}'


class ReverseGeocodingFile:
    """
    Class to fetch reverse geocoding data from a locally stored file.
    """
    def __init__(self, path: str):
        self._path = Path(path)


    def fetch_data(self) -> dict | None:
        """
        Attempts to open a given JSON file with reverse geocoding data and returns the data as a dictionary. Returns
        None if the file could not be accessed or if it is in the wrong format.
        """
        location_data = None

        try:
            location_data = self._path.open('r')

            return json.load(location_data)
        except OSError:
            _print_error(str(self._path.absolute()), 'MISSING')
            return None
        except json.JSONDecodeError:
            _print_error(str(self._path.absolute()), 'FORMAT')
            return None
        finally:
            if location_data != None:
                location_data.close()


def _print_error(first_arg: str, second_arg: str) -> None:
    """
    Prints the cause for error if an exception is raised.
    """
    print('FAILED')
    print(first_arg.strip())
    print(second_arg)