
# SatNOGS Collisions #

SatNOGS Collisions calculates physical and radio frequency proximity and collisions of space objects and transmitters.

## Installation
Clone the repository and to you local machine and install the requirements needed. 
```
$ git clone https://gitlab.com/librespacefoundation/satnogs/satnogs-collisions
$ pip3 install -r requirements.txt 
```

## Overview

This library consists of two major functionalities
* ***GSS Module*** - Detecting the RF collisions between the satellites at the GroundStation.
* ***Onlysat Module*** - Computing the region over which the Satellites may have an RF collision.

### GSS Module
This module provides methods to compute and  detect the collisions between the satellites at the Ground Station. 
```
from GSS import <method_name>
```
The methods provided by the GSS sub-module are as follows:
*  ***detect_RF_collision_of_satellite_over_groundstation*** - Detect  the collisions between satellites over a single Ground Station.
* ***detect_RF_collision_of_satellite_over_groundstations*** - Detect the collisions between the satellies over multiple Ground Stations.
* ***detect_RF_collision_of_satellites_over_groundstation*** - Detect the collisions between multiple satellites over a single Ground Station.
* ***detect_RF_collision_of_satellites_over_groundstations*** - Detect the collisions between multiple Satellites over multiple Ground Stations.
* ***compute_RF_collision_of_satellite_over_groundstation*** - Compute  the collisions between satellites over a single Ground Station
* ***compute_RF_collision_of_satellite_over_groundstations*** - Detect  the collisions between satellites over multiple single Ground Stations.
* ***compute_RF_collision_of_satellites_over_groundstation*** - Detect  the collisions between multiple satellites over a single Ground Station.
* ****compute_RF_collision_of_satellites_over_groundstations*** - Detect  the collisions between  multiple satellites over Ground Stations.

The ***compute_collisons*** methods mentioned above return the the RF collsions that contains metadata of the collisions like time_period, and satellites frequencies of the collision.

### OnlySat Module
This module provides methods to compute the region over which the Satellites may have an RF collision.
```
from only_sat import <method_name>
```
* ***detect_RF_collision_of_satellite_with_satellites*** - Detects the collision possible between a satellite with other satellites over any region given.
 * ***detect_RF_collision_of_satellites*** -  Detects the collision possible between a the given set of satellites with each other.
* ***detect_RF_collision_of_satellites_with_all_satellites*** - Detects the collision possible between a satellite with all other satellites resigstered under SATNOGS over any region given.
*  ***compute_RF_collision_of_satellite_with_satellites*** - Computes the collision possible between a satellite with other satellites over any region given.
* ***compute_RF_collision_of_satellites*** - Computes the collision possible between a the given set of satellites with each other.
* ***compute_RF_collision_of_satellites_with_all_satellites*** - Computes the collision possible between a satellite with all other satellites resigstered under SATNOGS over any region given.

The ***compute_collision*** methods in this submodule return the footprint and the frequecnies of the collisions as a metadata.

## Tests

To execute the tests run the following command in the current directory
```
$ python -m unittest tests/test
```

## License

[![license](https://img.shields.io/badge/license-AGPL%203.0-6672D8.svg)](LICENSE)
[![Libre Space Foundation](https://img.shields.io/badge/%C2%A9%202020-Libre%20Space%20Foundation-6672D8.svg)](https://librespacefoundation.org/)