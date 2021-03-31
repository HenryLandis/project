#!/usr/bin/env python

"""
Global variables.
"""

import os
import geopandas
import shapely

# global land cover used to subtract water from convex hull range sizes
LANDCOVER_FILE = os.path.join(
	os.path.dirname(os.path.dirname(__file__)), 
	"geojson",
	"land-cover.json",
)
LAND = shapely.geometry.MultiPolygon(
	geopandas.read_file(LANDCOVER_FILE).geometry.tolist()
)
