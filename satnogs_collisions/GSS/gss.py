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

def _compute_doppler_shift(sat, freq):
    """
    Computes the Maximum Doppler shift in the frequency at the ground station.
    Returns the Max and min doppler shifted frequencies received at the GroundStation.
    
    Arguments
    ===============================================
    sat: Ephem instance of the Satellites wrt the observer
    freq: Downlink frequencies transmitted by the satellite.
    """
    rel_vel = sat.range_velocity
    shift = (rel_vel/C)*(freq)
    freq_low_high = []
    # Append max and min frequencies shift to the list
    for elem in freq:
        freq_low_high.append(elem - shift)
        freq_low_high.append(elem)
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

        # Compute the next pass of the satellite over the observer
        satA.compute(observer)
        satB.compute(observer)

        # Check if the satellites' have a period of intersection
        intersection_range = _time_range_intersection(satA.rise_time, satA.set_time, satB.rise_time, satB.set_time)

        if intersection_range is not None:
            # Compute the Maximum and minimum Doppler frequencies
            # for all the frequencies for both the satellites
            freq1_low_high = _compute_doppler_shift(satA, sat1.get_frequencies())
            freq2_low_high = _compute_doppler_shift(satB, sat2.get_frequencies())
            if (_in_freq_range(freq1_low_high, freq2_low_high, frequency_range)):
                if (time_period):
                    return True
                time_periods.append(intersection_range)
        # Check for every increment after the minimum `set_time`
        e = ephem.Date(e + min(satA.set_time, satB.set_time) + ephem.minute)

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
                    date_time_range, frequency, time_period=time_period))
    return
