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
    freq_list = []
    for val1 in frequencies1:
        for val2 in frequencies2:
            if (abs(val2 - val1) <= frequency_range):
                freq_list.append((val1, val2))
    if len(freq_list):
        return freq_list
    return False

def _check_collision(sat1, sat2, date_time_range, time_accuracy, frequency_range, alpha=None, time_period=False, intersection=False):

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
            # Add previous recelty finished collision to the list
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

def detect_collisions(sats, main_sat, date_time_range, time_accuracy, frequency_range=30000, alpha=None, intersection=False):
    res = []
    for sat in sats:
        res.append(_check_collision(sat, main_sat, date_time_range, time_accuracy, frequency_range, alpha=alpha, time_period=False, intersection=intersection))
    return res

def compute_collisions(sats, main_sat, date_time_range, time_accuracy, frequency_range=30000, alpha=None, intersection=False):
    res = []
    for sat in sats:
        res.append(_check_collision(sat, main_sat, date_time_range, time_accuracy, frequency_range, alpha=alpha, time_period=True, intersection=intersection))
    return res