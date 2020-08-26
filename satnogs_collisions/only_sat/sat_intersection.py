import requests
import ephem
import geog
import math
import numpy as np
import shapely
import datetime
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from satnogs_collisions.satellite import Satellite

# Define Radius of Earth in m
R = 6371800

# Used when `detect_collisions_satellite`  method is called multiple times
all_sats = []

def _get_all_satellite():
    resonse = requests.get("https://db.satnogs.org/api/transmitters/")
    data = response.json()
    norad_ids = set()
    for sat_detail in data:
        norad_ids.add(sat_detail["norad_cat_id"])
    for norad_id in norad_ids:                                 # Get the list of all satellites
        frequencies = []
        for sat_detail in data:
            if (sat_detail["norad_cat_id"] == norad_id):
                frequencies.append(sat_detail["downlink_low"])
        sat = Satellite(norad_id=norad_id, frequencies=frequencies)
        all_sats.append(sat)
    return

def compute_intersection(footprint1, footprint2):
    """Compute the intersection of footprints using the `shapely` method.

    :param footprint1: footprint of the first satellite reprsented in a GeoJson format
    :type footprint1: Shapely polygon instance
    :param footprint2: footprint of the second satellite reprsented in a GeoJson format
    :type footprint2: Shapely polygon instance
    :return: intersection results of the footprint
    :rtype: Shapely polygon instance
    """
    res = footprint1.intersection(footprint2)
    return res

def compute_footprint(sat, date_time, alpha=None):
    """Compute the footprints of the Satellite at a given instance.

    :param sat: Satellite object
    :type sat: instance of the satnogs-collisions Satellite object
    :param date_time: desired date and time of the satellite footprint
    :type date_time: Python datetime object
    :param alpha: half angle given by user in degrees, defaults to None
    :type alpha: int, optional
    :return: Footprint of the Satllite in GeoJSON format
    :rtype: Shapely Polygon instance
    """

    # Read TLE of the sateellite and create an Ephem instance
    line1, line2, line3 = sat.get_tle()
    sat = ephem.readtle(line1, line2, line3)
    sat.compute(date_time)

    # Sub-satellite points
    sublat = sat.sublat
    sublong = sat.sublong

    # height of the satellite above sea level in m
    h = sat.elevation

    # Diameter of the circular coverage
    d = None
    if alpha:
        theta = math.degrees(math.asin(sin(alpha)*(R/(R+h)))) - alpha
        theta = math.radians(theta)
        # diameter
        d = 2*R*theta
    else:
        # Compute d as maximum d if alpha isn't defined
        rho = math.degrees(math.asin((R/(R+h))))
        lam = 90 - rho
        lam = math.radians(lam)
        d_max = R*(math.tan(lam))
        d = d_max

    # Convert the data to GeoJSON format
    p = Point([sublat, sublong])
    n = 32
    angles = np.linspace(0, 360, n)
    polygon = geog.propagate(p, angles, d)
    # footprint = {}
    # footprint["coordinates"] = polygon.tolist()
    # footprint["type"] = "Polygon"
    footprint = Polygon(list(polygon))
    return footprint

def _in_freq_range(frequencies1, frequencies2, frequency_range):
    """Check if difference between the frequencies lie in the given range
    """
    freq_list = []
    for val1 in frequencies1:
        for val2 in frequencies2:
            if (abs(val2 - val1) <= frequency_range):
                freq_list.append((val1, val2))
    if len(freq_list):
        return freq_list
    return False

def _check_collision(sat1, sat2, date_time_range, time_accuracy, frequency_range, alpha=None, time_period=False, intersection=False):
    """Helper function to check collision between Satellites in given time range.

    :param sat1: Satellite object
    :type sat1: instance of the satnogs-collisions Satellite object
    :param sat2: Satellite object
    :type sat2: instance of the satnogs-collisions Satellite object
    :param date_time_range: desired date and time of the satellite footprint
    :type date_time_range: Python datetime object
    :param time_accuracy: incrments of the time parameter in the given range to check for collisions in seconds
    :type time_accuracy: int
    :param frequency_range: frequency in Hz
    :type frequency_range: int
    :param alpha: half angle given by user in degrees, defaults to None
    :type alpha: int, optional
    :param time_period: parameter set to add time_period of the collisions to the Metadata, defaults to False
    :type time_period: bool, optional
    :param intersection: parameter set to add footprint of the collisions to the Metadata, defaults to False
    :type intersection: bool, optional
    :return: bool/ Array of time periods if there is a collision
    :rtype: bool/list
    """
    low = date_time_range[0]
    high = date_time_range[1]
    collisions = []
    # check frequencies
    freq_list = _in_freq_range(sat1.get_frequencies(), sat2.get_frequencies(), frequency_range)
    # Initialize buffers to store time_period, (timestamp,foorpint) tuples and collision dictionary
    tp = []
    time_fp = []
    temp = {}
    sat_arr = []
    # Add Satellites' Meta data to the dictionary
    if len(freq_list):
        sat_dict = {}
        sat_dict["norad_id"] = sat1.get_name().split(' ')[0]
        sat_dict["name"] = sat1.get_name().split(' ')[1]
        sat_dict["tle"] = sat1.get_tle()
        sat_dict["frequencies"] = sat1.get_frequencies()
        sat_dict["collision_frequencies"] = []
        for elem in freq_list:
            sat_dict["collision_frequencies"].append(elem[0])
        sat_arr.append(sat_dict)
        sat_dict = {}
        sat_dict["norad_id"] = sat2.get_name().split(' ')[0]
        sat_dict["name"] = sat2.get_name().split(' ')[1]
        sat_dict["tle"] = sat2.get_tle()
        sat_dict["frequencies"] = sat2.get_frequencies()
        sat_dict["collision_frequencies"] = []
        for elem in freq_list:
            sat_dict["collision_frequencies"].append(elem[1])
        sat_arr.append(sat_dict)
    # iterate throught he while loop only when frequencies are close
    while (len(freq_list) and low <= high):
        # Compute footprints each satellite
        fp1 = compute_footprint(sat1, low, alpha=alpha)
        fp2 = compute_footprint(sat2, low, alpha=alpha)
        # Compute footprints
        intersection_res = compute_intersection(fp1, fp2)
        if intersection_res:
            # Return true if metadata isn't required
            if not time_period:
                return True
            # no ongoing collision, add first new collision
            if not len(tp):
                # Start new collision and initialize metadata
                temp = {}
                temp["satellites"] = sat_arr
                tp = [low, low]
                if intersection:
                    time_fp.append((low, intersection_res))
            # add values to ongoing collision
            else:
                tp[-1] = low
                if intersection:
                    time_fp.append((low, intersection_res))
        else:
            # Add previous recenlty finished collision to the list
            if (len(tp)):
                temp["time_period"] = tp
                if intersection:
                    temp["footprints"] = time_fp
                collisions.append(temp)
                # Initialize values for new collisions
                tp = []
                time_fp = []
                temp = {}
        low += datetime.timedelta(seconds=time_accuracy)
    temp["time_period"] = tp
    if intersection:
        temp["footprints"] = time_fp
    collisions.append(temp)
    if not time_period:
        return False
    return collisions

def detect_RF_collision_of_satellite_with_satellites(sats, main_sat, date_time_range, time_accuracy, frequency_range=30000, alpha=None):
    """Detects if there is a collision possible between main_sat and other satellites over any region given the date_time_range and the satelitte details

    :param sats: List of Satellites
    :type sats: list
    :param main_sat: Satellite
    :type main_sat: Instance of `Satellite`
    :param date_time_range: User defined date-time range
    :type date_time_range: datetime
    :param time_accuracy: incrments of the time parameter in the given range to check for collisions in seconds
    :type time_accuracy: int
    :param frequency_range: Frequency in Hz, defaults to 30000
    :type frequency_range: int, optional
    :param alpha: half angle given by user in degrees, defaults to None
    :type alpha: int, optional
    :param intersection: parameter set to add footprint of the collisions to the Metadata, defaults to False
    :type intersection: bool, optional
    :return: list boolean values of collisions between satellites
    :rtype: list
    """
    res = []
    for sat in sats:
        res.append(_check_collision(sat, main_sat, date_time_range, time_accuracy, frequency_range, alpha=alpha, time_period=False, intersection=intersection))
    return res

def detect_RF_collision_of_satellites(sats, date_time_range, time_accuracy, frequency_range=30000, alpha=None):
    """Detects the collision possible between every sat with all other satellites over any region given the date_time_range and the satelitte details

    :param sats: List of all Satellites
    :type sats: list
    """
    all_collisions = {}
    for main_sat in sats:
        sat_list = []
        for sat in sats:
            if sat != main_sat:
                sat_list.append(sat)
        res = detect_collisions_satellite(sat_list, main_sat, date_time_range, time_accuracy, frequency_range=frequency_range, alpha=alpha, intersection=intersection)
        all_collisions[main_sat.get_name()] = res

def detect_RF_collision_of_satellite_with_all_satellites(sat, date_time_range, time_accuracy, frequency_range=30000, alpha=None):
    """Detects collisions of one satellite with all the other satellites in the Network.

    :param sat: The one satellite we desire to compare with
    :type sat: Satellite instance

    """
    if not len(all_sats):
        _get_all_satellite()
    detect_collisions_satellites(all_sats, sat, date_time_range, time_accuracy, frequency_range=frequency_range, alpha=alpha)

def compute_RF_collision_of_satellite_with_satellites(sats, main_sat, date_time_range, time_accuracy, frequency_range=30000, alpha=None, intersection=False):
    """Computes the collision possible between main_sat and other satellites over any region given the date_time_range and the satelitte details

    :param sats: List of Satellites
    :type sats: list
    :param main_sat: Satellite
    :type main_sat: Instance of `Satellite`
    :param date_time_range: User defined date-time range
    :type date_time_range: datetime
    :param time_accuracy: incrments of the time parameter in the given range to check for collisions in seconds
    :type time_accuracy: int
    :param frequency_range: Frequency in Hz, defaults to 30000
    :type frequency_range: int, optional
    :param alpha: half angle given by user in degrees, defaults to None
    :type alpha: int, optional
    :param intersection: parameter set to add footprint of the collisions to the Metadata, defaults to False
    :type intersection: bool, optional
    :return: Array of collisions containing the metadate of each collision along with it
    :rtype: list
    """
    res = []
    for sat in sats:
        res.append(_check_collision(sat, main_sat, date_time_range, time_accuracy, frequency_range, alpha=alpha, time_period=True, intersection=intersection))
    return res

def compute_RF_collision_of_satellites(sats, date_time_range, time_accuracy, frequency_range=30000, alpha=None, intersection=False):
    """Computes the collision possible between every sat with all other satellites over any region given the date_time_range and the satelitte details

    :param sats: List of all Satellites
    :type sats: list
    """
    all_collisions = {}
    for main_sat in sats:
        sat_list = []
        for sat in sats:
            if sat != main_sat:
                sat_list.append(sat)
        res = compute_collisions_satellite(sat_list, main_sat, date_time_range, time_accuracy, frequency_range=frequency_range, alpha=alpha, intersection=intersection)
        all_collisions[main_sat.get_name()] = res
    
def compute_RF_collision_of_satellite_with_all_satellites(sat, date_time_range, time_accuracy, frequency_range=30000, alpha=None):
    """Computes collisions of one satellite with all the other satellites in the Network.

    :param sat: The one satellite we desire to compare with
    :type sat: Satellite instance

    """
    if not len(all_sats):
        _get_all_satellite()
    compute_collisions_satellites(all_sats, sat, date_time_range, time_accuracy, frequency_range=frequency_range, alpha=alpha)
