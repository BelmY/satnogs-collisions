import ephem
import geog
import math
import numpy as np
import shapely
from satnogs_collisions.satellite import Satellite

# Define Radius of Earth in m
R = 6371800

def compute_intersection(footprint1, footprint2):
    res = footprint1.intersection(footprint2)
    return res

def compute_footprint(sat, date_time, alpha=None):

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
    p = shapely.geometry.Point([sublat, sublong])
    n = 32
    angles = np.linspace(0, 360, n)
    polygon = geog.propagate(p, angles, d)
    # footprint = {}
    # footprint["coordinates"] = polygon.tolist()
    # footprint["type"] = "Polygon"
    footprint = shapely.Polygon(polygon.tolist())

    return footprint

def _in_freq_range(frequencies1, frequencies2, frequency_range):
    freq_list = []
    for val1 in frequencies1:
        for val2 in frequencies2:
            if (abs(val2 - val1) <= frequency_range):
                freq_list.append((val1, val2))
    if len(freq_list):
        return freq_list
    return False

def convert_dic(collisions, time_accuracy):

    sat_set = set()
    for dic in collisions:
        arr_set.add(dic["satellites"])
    # Array for updated collisions format
    updated_cols = []
    for sat_data in sat_set:
        # Store all the footprints
        footprints = []
        for dic in collisions:
            if (dic["satellites"] = sat_data):
                footprints.append((dic["time_stamp"], dic["footprint"]))
        # should be divided into subarrays if there are mutiple collisions
        # spread apart within the given time range of different time_periods 
        footprint_subarr = []
        start_time = None
        count = 0
        for fp in footprints:
            if start_time is None:
                start_time = fp[0]
            if ((fp[0] - start_time) == count*time_accuracy):
                footprint_subarr.append(fp)
            else:
                # Current time would be the end time of the collision
                end_time = fp[0]
                footprint_subarr.append(fp)
                temp = {}
                temp["satellites"] = sat_data
                temp["time_period"] = [start_time, end_time]
                temp["footprints"] = footprint_subarr
                updated_cols.append(temp)
                # Reinitialize the variables to check for another collision
                # in the given range if any
                footprint_subarr.clear()
                start_time = None
                count = 0
    return updated_cols

def _check_collision(sat1, sat2, date_time_range, time_accuracy, frequency_range, alpha=None, intersection=False):

    low = date_time_range[0]
    high = date_time_range[1]
    collisions = []
    while (low <= high):
        # Compute footprints and get transponder frequecies of each satellite
        footprints = []
        footprints.append(compute_footprint(sat1, low, alpha=alpha))
        footprints.append(compute_footprint(sat2, low, alpha=alpha))
        # Compute footprints
        intersection_res = compute_intersection(footprints)
        if intersection_res:
            # check frequencies
            freq_list = _in_freq_range(sat1.get_frequencies(), sat2.get_frequencies(), frequency_range)
            if (len(freq_list)):
                if not intersection:
                    return True
                temp = {}
                temp["satellites"] = []
                # Add Satellites' Meta data to the dictionary
                sat_dict = {}
                sat_dict["norad_id"] = sat1.get_name().split(' ')[0]
                sat_dict["name"] = sat1.get_name().split(' ')[1]
                sat_dict["tle"] = sat1.get_tle()
                sat_dict["frequencies"] = sat1.get_frequencies()
                sat_dict["collision_frequencies"] = []
                for elem in freq_list:
                    sat_dict["collision_frequencies"].append(elem[0])
                temp["satellites"].append(sat_dict)
                sat_dict = {}
                sat_dict["norad_id"] = sat2.get_name().split(' ')[0]
                sat_dict["name"] = sat2.get_name().split(' ')[1]
                sat_dict["tle"] = sat2.get_tle()
                sat_dict["frequencies"] = sat2.get_frequencies()
                sat_dict["collision_frequencies"] = []
                for elem in freq_list:
                    sat_dict["collision_frequencies"].append(elem[1])
                temp["satellites"].append(sat_dict)
                # Add time period of the collision
                temp["time_stamp"] = low
                temp["footprint"] = intersection_res
                collisions.append(temp)
        low += time_accuracy
    if not intersection_res:
        return False
    collisions = convert_dic(collisions, time_accuracy)
    return collisions

def detect_collisions(sats, main_sat, date_time_range, time_accuracy, frequency_range=30000, alpha=None):
    res = []
    for sat in sats:
        res.append(_check_collision(sat, main_sat, date_time_range, time_accuracy, frequency_range, alpha=alpha, intersection=False))
    return res

def compute_collisions(sats, main_sat, date_time_range, time_accuracy, frequency_range=30000, alpha=None):
    res = []
    for sat in sats:
        res.append(_check_collision(sat, main_sat, date_time_range, time_accuracy, frequency_range, alpha=alpha, intersection=True))
    return res