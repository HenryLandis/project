#!/usr/bin/env python

"""
Global variables.
"""

import geopandas
import shapely

# global land cover used to subtract water from convex hull range sizes
_lands = geopandas.read_file("../geojson/land-cover.json")
LAND = shapely.geometry.MultiPolygon(_lands.geometry.tolist())
