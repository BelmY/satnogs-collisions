import ephem
from satnogs_collisions.satellite import Satellite
from satnogs_collisions.ground_station import GroundStation

# Define speed of light
C = 299792458.0

def _time_range_intersection(sat1_rise, sat1_set, sat2_rise, sat2_set):
    """
    Computes the intersection of the rise and set time intervals of the 2 satellites.
    Returns None if there is no intersection.

    Arguments
    ============
    sat1_rise: Rise time of the first satellite
    sat1_set: Set time of the first satellite
    sat2_rise: Rise time of the second satellite
    sat2_set: Set time of the second satellite
    """
    low = max(sat1_rise, sat2_rise)
    high = min(sat1_set, sat2_set)
    if (low <= high):
        return low,high
    return

def _compute_doppler_shift(sat, observer, freq, rise_time, set_time):
    """
    Computes the Maximum Doppler shift in the frequency at the ground station.
    Returns the Max and min doppler shifted frequencies received at the GroundStation.
    
    Arguments
    ===============================================
    sat: Ephem instance of satellite
    observer: Ephem instance of Observer
    freq: List of downlink frequencies transmitted by the satellite
    rise_time: Rise time of satellite's next pass wrt the observer
    set_time: Set time of satellite's next pass wrt the observer
    """
     # Maximum shift observed at Rise time
    observer.date = rise_time
    sat.compute(observer)
    rel_vel = sat.range_velocity
    shift_r = (rel_vel/C)*(freq)
     # Maximum shift observed at Rise time
    observer.date = set_time
    sat.compute(observer)
    rel_vel = sat.range_velocity
    shift_s = (rel_vel/C)*(freq)
    # Append max and min frequencies shift to the list
    freq_low_high = []
    for elem in freq:
        freq_low_high.append(elem - shift_r)
        freq_low_high.append(elem + shift_s)
    return freq_low_high

def _in_freq_range(frequencies1, frequencies2, range):
    """
    Checks if the frequencies of both the satellites fall under the given range.

    Arguments
    =======================================
    frequencies1, frequencies2: list of the low and high doppler shifted frequencies of the satellites
    range = Given frequecny range in Hz
    """
    # Swap according to the smaller list.
    if (len(frequencies2) < len(frequencies1)):
        temp = frequencies[2]
        frequencies[2] = frequencies[1]
        frequencies[1] = temp
    
    # compare all the frequencies
    for freq1 in frequencies1:
        for freq2 in frequencies2:
            if (abs(freq2 - freq1) <= range):
                return True
    return False   

def _check_collision(ground_station, sat1, sat2, date_time_range, frequency_range, time_period=False):
    """
    Checks and computes the possible collision between sat1 and sat2

    Arguments
    =======================================================
    ground_station: Instance of the `GroundStation` class
    sat1: First satellite, instance of the `Satellite` class
    sat2: Second satellite, instance of the `Satellite` class
    date_time_range : datatime list of size 2 representing the desirable interval.
    frequency_range : real rumber range of the frequency (in Hz)
    time_period: Set to true when the user desires to compute the time periods instead of 
                just checking the RF Collisions.
    """

    # Extract ground coordinates
    ground_coordinates = ground_station.get_coordinates()
    # Define an Epem Observer
    observer = ephem.Observer()
    observer.elevation = ground_station.get_elevation()
    observer.lat = ground_coordinates[0]
    observer.lon = ground_coordinates[1]

    # Read TLE of both the sateellites and create an instance
    line1, line2, line3 = sat1.get_tle()
    satA = ephem.readtle(line1, line2, line3)
    line1, line2, line3 = sat2.get_tle()
    satB = ephem.readtle(line1, line2, line3)

    # This stores an array of intervals as there could be multiple RF collisions 
    # between the  satellites at the given time interval. 
    time_periods = []

    # Convert the date_time interval to ephem Date instances
    e_low = ephem.Date(date_time_range[0])
    e_high = ephem.Date(date_time_range[1])
    e = e_low
    while (e <= e_high):
        # Set the date and time of the oberserver
        observer.date = e

        # `next_pass` computes the rise_time, Rise azimuth ,maximum_atlitude,
        # max_altitude_time, set_time and set Azimuth of the Satellite.
        infoA = observer.next_pass(satA)
        infoB = observer.next_pass(satB)

        # Check if the satellites' have a period of intersection
        intersection_range = _time_range_intersection(infoA[0], infoA[4], infoB[0], infoB[4])

        if intersection_range is not None:
            # Compute the Maximum and minimum Doppler frequencies
            # for all the frequencies for both the satellites
            freq1_low_high = _compute_doppler_shift(satA, observer, sat1.get_frequencies(), infoA[0], infoA[4])
            freq2_low_high = _compute_doppler_shift(satB, observer, sat2.get_frequencies(), infoB[0], infoB[4])
            if (_in_freq_range(freq1_low_high, freq2_low_high, frequency_range)):
                if (time_period):
                    return True
                time_periods.append(intersection_range)
        # Check for every increment after the minimum `set_time`
        e = ephem.Date(e + min(infoA[4], infoB[4]) + ephem.minute)

    # Return True or time_periods depending on the passed argument `time_period`
    if (len(time_periods) == 0):
        return False
    return time_periods


def detect_RF_collision_of_satellite_over_groundstation(ground_station, 
                    satellites, main_sat, date_time_range, frequency_range=30000, time_period=False):
    """
    Detects the RF collisions that main satellite will have
    with other satellites over the ground station.

    Returns
    ===================
    If time_period = `True`:
    * Returns that time periods of all (main_sat, other_sat) if an RF collision occurs
    * The pairs value is set to None in case of no collision

    If time_period = `False`:
    * Returns an array of  booleans indicating if a collision is possible.

    Arguments
    ==========================================================
    ground_station : instance of the object `GroundStation`
    satellites : array of instances of the object `Satellite`
    main_sat : instance of object `Satellite`
    date_time_range : datatime list of size 2 representing the desirable interval.
    frequency_range : real rumber range of the frequency (in KHz)
    time_period: Set to true when the user desires to compute the time periods instead of 
                just checking the RF Collisions.
    """
    rf_collisions = []
    for sat in satellites:
            rf_collisions.append(_check_collision(ground_station, main_sat, sat, 
                    date_time_range, frequency_range, time_period=time_period))
    return rf_collisions

def detect_RF_collision_of_satellite_over_groundstations(ground_stations, 
                    satellites, main_sat, date_time_range, frequency_range=30000, time_period=False):
    """
    Detects the RF collisions that main satellite will have
    with other satellites over each ground station.

    Returns: A dictionary of that contains collision over each ground station.

    Arguments
    ==========================================================
    ground_stations : List of instances of the object `GroundStation`
    """
    all_rf_collisions = {}
    # Ground Station index for the dictionary.
    id = 1
    for ground_station in ground_stations:
        rf_collisions = []
        for sat in satellites:
                rf_collisions.append(_check_collision(ground_station, main_sat, sat, 
                        date_time_range, frequency_range=frequency_range, time_period=time_period))
        all_rf_collisions[id] = rf_collisions
        id += 1
    return all_rf_collisions

def detect_RF_collision_of_satellites_over_groundstation(ground_station, 
                    satellites, date_time_range, frequency_range=30000, time_period=False):
    """
    Detects the RF collisions that every pair of satellite will
    have with each other over the ground station.

    Returns: A dictionary of <satellite_name, List> which contains collisions over a groundstation

    Arguments
    ==========================================================
    ground_station : instance of the object `GroundStation`
    satellites : List of instances of the object `Satellite`
    """
    all_rf_collisions = {}
    for main_sat in satellites:
        # Create a satellite list to pass to `detect_RF_collision_of_satellite_over_groundstation`
        sat_list  = []
        for sat in satellites:
            if (sat != main_sat):
                sat_list.append(sat)
        all_rf_collisions[main_sat.get_name()] = (detect_RF_collision_of_satellite_over_groundstation(ground_station, sat_list, main_sat,
                                               date_time_range, frequency_range=frequency_range, time_period=time_period))
    return all_rf_collisions

def detect_RF_collision_of_satellites_over_groundstations(ground_stations, 
                    satellites, date_time_range, frequency_range=30000, time_period=False):
    """
    Detects the RF collisions that each pair of satellite will have
    with one another over  each ground station.

    Returns: A dictionary <ground_station_name, dictionary> that contains RF collisions of all GSS pairs.
 
    Arguments
    ==========================================================
    ground_stations : List of instances of the object `GroundStation`
    satellites : List of instances of the object `Satellite`
    """
    all_rf_collisions = {}
    # Ground Station index for the dictionary.
    id = 1
    for ground_station in ground_stations:
        all_rf_collisions[id] = (detect_RF_collision_of_satellites_over_groundstation(ground_station, satellites, date_time_range,
                         frequency_range=frequency_range, time_period=time_period))
        id += 1
    return all_rf_collisions

def compute_RF_collision_of_satellite_over_groundstation(ground_station, 
                    satellites, main_sat, date_time_range, frequency_range=30000):
    """
    Computes the time periods of the RF collisions that main satellite will have
    with other satellites over the ground station.

    Arguments
    ==========================================================
    ground_station : instance of the object `GroundStation`
    satellites : array of instances of the object `Satellite`
    main_sat : instance of object `Satellite`
    date_time_range : datatime list of size 2 representing the desirable interval.
    frequency_range : real rumber range of the frequency (in KHz)
    """
    return detect_RF_collision_of_satellite_over_groundstation(ground_station, 
                    satellites, main_sat, date_time_range, frequency_range=frequency_range, time_period=True)

def compute_RF_collision_of_satellite_over_groundstations(ground_stations, 
                    satellites, main_sat, date_time_range, frequency_range=30000):
    """
    Computes the time periods of the RF collisions that every pair of satellite will
    have with each other over the ground station.

    Returns: A dictionary which contains the time period of collisions over every ground station.
    """
    return detect_RF_collision_of_satellite_over_groundstations(ground_stations, 
                    satellites, main_sat, date_time_range, frequency_range=frequency_range, time_period=True)

def compute_RF_collision_of_satellites_over_groundstation(ground_station, 
                    satellites, date_time_range, frequency_range=30000, time_period=False):
    """
    Computes the time periods of the RF collisions that every pair of satellite will
    have with each other over the ground station.

    Returns: A dictionary of <satellite_name, List> which contains time periods of RF collisions over a groundstation.
    """
    return detect_RF_collision_of_satellites_over_groundstation(ground_station, 
                    satellites, date_time_range, frequency_range=frequency_range, time_period=True)

def Computes_RF_collision_of_satellites_over_groundstations(ground_stations, 
                    satellites, date_time_range, frequency_range=30000, time_period=False):
    """
    Computes the time periods of the RF collisions that each pair of satellite will have
    with one another over  each ground station.

    Returns: A dictionary <ground_station_name, dictionary> that contains time periods of RF RF collisions of all GSS pairs.
    """"
    return detect_RF_collision_of_satellites_over_groundstations(ground_stations, 
                    satellites, date_time_range, frequency_range=frequency_range, time_period=True)