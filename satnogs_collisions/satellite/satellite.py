import requests
from satellite_tle import fetch_tle_from_celestrak

def _set_tle(norad_id):
    tle = fetch_tle_from_celestrak(norad_id)
    return tle

def _set_frequencies(norad_id):
    response = requests.get("https://db.satnogs.org/api/transmitters/?satellite__norad_cat_id=" + str(norad_id))
    data = response.json()
    downlink_lows = set()
    for elem in data:
        downlink_lows.add(elem["downlink_low"])
    # Return a list for easy access of elements
    return list(downlink_lows)

class Satellite:
    """Class for the Satellite objects.

    :param norad_id: Satellite NORAD ID, defaults to None
    :type norad_id: int, optional
    :param tle: Two line elemnet set, defaults to []
    :type tle: list, optional
    :param frequencies: Transmitting frequencies of the Satellite, defaults to None
    :type frequencies: list, optional
    :raises ValueError: Missing values
    """
    def __init__(self, norad_id=None, tle=[], frequencies=None):
        """Constructor method
        """
        self.norad_id = norad_id
        if (len(tle) == 3 and frequencies):
            self.tle = tle
            self.frequencies = frequencies
        elif (norad_id):
            self.tle = _set_tle(norad_id)
            if not frequencies:
                self.frequencies = _set_frequencies(norad_id)
            else:
                self.frequencies = frequencies
        else:
            raise ValueError("Values Missing. Must provide either the 'Norad ID' or the 'TLE and frequency' of satellite")

    def get_tle(self):
        return self.tle

    def get_frequencies(self):
        return self.frequencies
    
    def get_name(self):
        return self.tle[0]
