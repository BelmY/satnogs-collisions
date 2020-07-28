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

    # if (alpha is None):
    #     # Compute for alpha

    # Read TLE of the sateellite and create an Ephem instance
    line1, line2, line3 = sat1.get_tle()
    sat = ephem.readtle(line1, line2, line3)
    sat.compute(date_time)

    # Sub-satellite points
    sublat = sat.sublat
    sublong = sat.sublong

    # height of the satellite above sea level in m
    h = sat.elevation

    # Compute the diameter of the circular coverage
    theta = math.degrees(math.asin(sin(alpha)*(R/(R+h)))) - alpha
    theta = math.radians(theta)
    # diameter
    d = 2*R*theta

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

def _check_collision(sat1, sat2, date_time_range, time_accuracy, frequency_range=30000, intersection=False):
    
    low = date_time_range[0]
    high = date_time_range[1]
    collisions = []
    while (low < high):
        # Compute footprints and get transponder frequecies of each satellite
        footprints = []
        footprints.append(compute_footprint(sat1))
        footprints.append(compute_footprint(sat2))\
        # Compute footprints
        intersection_res = compute_intersection(footprints)
        if intersection_res:
            # check frequencies
            freq_list = _in_freq_range(sat1.get_frequencies(), sat2.get_frequencies(), frequency_range)
            if (len(freq_list)):
                if not intersection:
                    return True
                temp = {}
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
    return collisions

def detect_collisions(sats, main_sat, date_time_range, time_accuracy, frequency_range):
    res = []
    for sat in sats:
        res.append(_check_collision(sat, main_sat, date_time_range, time_accuracy, frequency_range=frequency_range, intersection=False))
    return res

def compute_collisions(sats, main_sat, date_time_range, time_accuracy, frequency_range):
    res = []
    for sat in sats:
        res.append(_check_collision(sat, main_sat, date_time_range, time_accuracy, frequency_range=frequency_range, intersection=True))
    return res