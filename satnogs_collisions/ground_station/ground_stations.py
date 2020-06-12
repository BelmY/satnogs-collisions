import requests
import warnings

def _set_params(ground_station_id):
    response = requests.get("https://network.satnogs.org/api/stations/?id=" + str(ground_station_id))
    data = response.json()
    return data[0]['lat'], data[0]['lng'], data[0]['altitude']

class GroundStation:
    '''
    Class for the ground stations
    
    Arguments to the constructor 
    ============================================
    ground_station_id: An integer indicating the 'id' of the desired Ground Station
    coordinates: A 2-tuple/list giving the coordinates of the Ground Station
    elevation: Elevation of the ground station (in meters)

    Examples
    ==============================================
    >> from satnogs_collisions import GroundStation
    >> gs = GroundStation(2)
    >> gs.get_coordinates()
    [39.236, -86.305]
    >> gs.get_elevation()
    280
    '''
    def __init__(self, ground_station_id=None, coordinates=[], elevation=None):
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
