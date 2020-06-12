import requests
from satellite_tle import fetch_tle_from_celestrak

def _set_tle(norad_id):
    tle = fetch_tle_from_celestrak(norad_id)
    return tle

def _set_frequencies(norad_id):
    response = requests.get("https://db.satnogs.org/api/transmitters/")
    data = response.json()
    downlink_lows = set()
    for elem in data:
        downlink_lows.add(elem["downlink_low"])
    # Return a list for easy access of elements
    return list(downlink_lows)

class Satellite:
    '''
    Class for the satellies objects.
    
    Arguments to the constructor
    =================================
    norad_id: Represents the norad_cat_ID of the satellite. Must be an integer
    tle: A 3-tuple containing the TLE of the Satellite
    frequency: The transmitting frequencies of the Satellite.

    Examples
    ==================
    >> from satnogs_collisions import Satellite
    >> sat = Satellite(27844)
    >> sat.get_tle()
    ('CUTE-1 (CO-55)', '1 27844U 03031E   20161.76401087  .00000028  00000-0  32030-4 0  9997', 
    '2 27844  98.6813 169.6158 0011130  79.4057 280.8373 14.22241423879006')
    >> sat.get_frequencies()
    437470000
    '''
    def __init__(self, norad_id=None, tle=[], frequency=None):
        self.norad_id = norad_id
        if (len(tle) == 3 and frequencies):
            self.tle = tle
            self.frequencies = frequencies
        elif (norad_id):
            self.tle = _set_tle(norad_id)
            self.frequencies = _set_frequencies(norad_id)
        else:
            raise ValueError("Values Missing. Must provide either the 'Norad ID' or the 'TLE and frequency' of satellite")

    def get_tle(self):
        return self.tle

    def get_frequencies(self):
        return self.frequencies
