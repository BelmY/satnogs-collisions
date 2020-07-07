from satnogs_collisions import Satellite, GroundStation, detect_RF_collision_of_satellite_over_groundstation, compute_RF_collision_of_satellite_over_groundstation
import datetime as dt
import unittest

def _check_in_range(dt_range, obv):
    if (dt_range[0] <= obv[0] and dt_range[1] >= obv[1]):
        return True
    return False

class TestCollisions(unittest.TestCase):
    def test_collision_inside_time_range(self):
        """Collision lies inside start_datetime and end_datetime
        """
        tle = [
        "44369 - ACRUX-1",
        "1 44369U 19037E   20089.60368814  .00003999  00000-0  10277-3 0  9991",
        "2 44369  45.0135 203.0050 0012243  71.8742 288.3475 15.41070061 42252"
        ]
        frequencies = [437420000, 437420000]
        main_sat = Satellite(tle=tle, frequencies=frequencies)

        tle = ["40014 - BUGSAT-1",
        "1 40014U 14033E   20089.83608613  .00000338  00000-0  36005-4 0  9996",
        "2 40014  98.0547  49.3997 0031228 193.5632 166.4767 14.95418473315114"
        ]
        frequencies = [437445000]
        other_sat = [Satellite(tle=tle,frequencies=frequencies)]

        gs = GroundStation(6)

        dt_range = [dt.datetime(2020,3,30,0,0), dt.datetime(2020,3,30,2, 0)]

        collision =  compute_RF_collision_of_satellite_over_groundstation(gs, other_sat, main_sat, dt_range)
        collision_range = collision[0][1]['time_period']
        in_range = _check_in_range(dt_range, collision_range)
        self.assertEqual(in_range, True)
    
    def test_collision_ends_after_endtime(self):
        """Collision ends after end_datetime
        """
        tle = [
        "29499 - METOP-A",
        "1 29499U 06044A   20166.20046846 -.00000013  00000-0  13512-4 0  9993",
        "2 29499  98.5222 213.1022 0000717  97.5352 334.4680 14.21499803708240"
        ]
        frequencies = [1701300000, 465988000, 1544500000]
        main_sat = Satellite(tle=tle, frequencies=frequencies)

        tle = ["39086 - SARAL",
        "1 39086U 13009A   20166.17283789 -.00000009 +00000-0 +12852-4 0  9991",
        "2 39086 098.5437 351.7893 0000311 105.9251 254.1967 14.32027689381534"
        ]
        frequencies = [465988000]
        other_sat = [Satellite(tle=tle,frequencies=frequencies)]

        gs = GroundStation(1376)

        dt_range = [dt.datetime(2020, 6, 14, 19, 47), dt.datetime(2020, 6, 14, 19, 59)]

        collision =  compute_RF_collision_of_satellite_over_groundstation(gs, other_sat, main_sat, dt_range)
        collision_range = collision[0][1]['time_period']
        in_range = _check_in_range(dt_range, collision_range)
        
        self.assertEqual(in_range, True)
    
    def test_collision_starts_before_starttime(self):
        """Collision begins before start_datetime
        """
        tle = [
        "45258 - Phoenix (ASU)",
        "1 45258U 98067RB  20067.47769304  .00002942  00000-0  59624-4 0  9996",
        "2 45258  51.6418 131.6319 0006369 330.6920  29.3711 15.49954130  2659"
        ]
        frequencies = [437350000]
        main_sat = Satellite(tle=tle, frequencies=frequencies)

        tle = ["45263 - QARMAN",
        "1 45263U 98067RG  20067.47843361  .00002564  00000-0  53131-4 0  9995",
        "2 45263  51.6423 131.6371 0007933 343.6105  16.4627 15.49877689  2719"
        ]
        frequencies = [437350000]
        other_sat = [Satellite(tle=tle,frequencies=frequencies)]

        gs = GroundStation(173)

        dt_range = [dt.datetime(2020,3,9, 2, 28), dt.datetime(2020, 3, 9, 2, 42)]

        collision =  compute_RF_collision_of_satellite_over_groundstation(gs, other_sat, main_sat, dt_range)
        collision_range = collision[0][1]['time_period']
        in_range = _check_in_range(dt_range, collision_range)
        
        self.assertEqual(in_range, True)
    
    def test_time_range_inside_collision_range(self):
        """dt_range lies inside Observation range
        """
        tle = [
        "44365 - PAINANI-1",
        "1 44368U 19037D   19198.45401006 -.00000346  00000-0  00000+0 0  9996",
        "2 44368  45.0099 187.8591 0013817  14.6820 345.4487 15.38804178  2815"
        ]
        frequencies = [437475000]
        main_sat = Satellite(tle=tle, frequencies=frequencies)

        tle = [
        "39469 - MCUBED-2",
        "1 39469U 13072H   19196.38063689 +.00000638 +00000+0 +81383-4 0  6599",
        "2 39469 120.4920  58.6451 0247670 268.5966  88.6703 14.78448918111737"
        ]
        frequencies = [437480000]
        other_sat = [Satellite(tle=tle,frequencies=frequencies)]

        gs = GroundStation(488)


        dt_range = [dt.datetime(2019, 7, 18, 5, 51), dt.datetime(2019, 7, 18, 5, 55)]

        collision =  compute_RF_collision_of_satellite_over_groundstation(gs, other_sat, main_sat, dt_range)
        collision_range = collision[0][1]['time_period']
        in_range = _check_in_range(collision_range, dt_range)
        
        self.assertEqual(in_range, True)
    
    def test_high_level_collisions(self):
        """High level collisions
        """
        tle = [
        "44359 - TBEX-B",
        "1 44359U 19036W   19222.47268441  .00037674  00000-0  53867-3 0  9995",
        "2 44359  28.5237 259.8003 0385299 234.5596 121.8440 15.00094124  6777"
        ]
        frequencies = [399968000, 149988000, 437535000, 437485000]
        main_sat = Satellite(tle=tle, frequencies=frequencies)

        tle = [
        "43616 - ELFIN B",
        "1 43616U 18070D   19222.11284429  .00002592  00000-0  68524-4 0  9990",
        "2 43616  93.0213  25.1996 0019528 104.5693 255.7729 15.38297338 50477"
        ]
        frequencies = [437475000, 437475000]
        other_sat = [Satellite(tle=tle,frequencies=frequencies)]

        coordinates = [24.771, 46.708]
        elevation = 612

        gs = GroundStation(coordinates=coordinates, elevation=elevation)

        dt_range = [dt.datetime(2019, 8, 11, 00, 28), dt.datetime(2019, 8, 11, 00, 48)]

        collision =  compute_RF_collision_of_satellite_over_groundstation(gs, other_sat, main_sat, dt_range)
        collision_range = collision[0][1]['time_period']
        in_range = _check_in_range(dt_range, collision_range)

        self.assertEqual(in_range, True)
    
    
    def test_no_collision_inside_time_range(self):
        """No Collision occurs in the given time range
        """
        tle = [
        "44359 - TBEX-B",
        "1 44359U 19036W   19222.47268441  .00037674  00000-0  53867-3 0  9995",
        "2 44359  28.5237 259.8003 0385299 234.5596 121.8440 15.00094124  6777"
        ]
        frequencies = [399968000, 149988000, 437535000, 437485000]
        main_sat = Satellite(tle=tle, frequencies=frequencies)

        tle = [
        "43616 - ELFIN B",
        "1 43616U 18070D   19222.11284429  .00002592  00000-0  68524-4 0  9990",
        "2 43616  93.0213  25.1996 0019528 104.5693 255.7729 15.38297338 50477"
        ]
        frequencies = [437475000, 437475000]
        other_sat = [Satellite(tle=tle,frequencies=frequencies)]

        coordinates = [24.771, 46.708]
        elevation = 612

        gs = GroundStation(coordinates=coordinates, elevation=elevation)

        dt_range = [dt.datetime(2019, 8, 11, 00, 55), dt.datetime(2019, 8, 11, 00, 59)]

        collision =  detect_RF_collision_of_satellite_over_groundstation(gs, other_sat, main_sat, dt_range)
        self.assertEqual(collision[0], False)
