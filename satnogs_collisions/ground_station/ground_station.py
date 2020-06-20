import requests
import warnings

def _set_params(ground_station_id):
    response = requests.get("https://network.satnogs.org/api/stations/?id=" + str(ground_station_id))
    data = response.json()
    return data[0]['lat'], data[0]['lng'], data[0]['altitude']

class GroundStation:
    """Class for Ground-stations

    :param ground_station_id: ID of the ground Station, defaults to None
    :type ground_station_id: int, optional
    :param coordinates: coordinates of the Ground Station, defaults to []
    :type coordinates: list, optional
    :param elevation: elevation of theGround Station, defaults to None
    :type elevation: int, optional
    :raises ValueError: Missing Values
    """
    def __init__(self, ground_station_id=None, coordinates=[], elevation=None):
        """Constructor method
        """
        self.ground_station_id = ground_station_id
        if (len(coordinates) == 2 and elevation):
            self.latitude = coordinates[0]
            self.longitide = coordinates[1]
            self.elevation = elevation
        elif (ground_station_id):
            self.latitude, self.longitide, self.elevation = _set_params(ground_station_id)
        else:
            raise ValueError("Values Missing. Must provide either the 'GroundStation ID' or"  
                                     "the 'coordinates and elevation' of  the ground station")

    def get_coordinates(self):
        return (self.latitude, self.longitide)
    
    def get_elevation(self):
        return self.elevation
