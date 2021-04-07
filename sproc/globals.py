#!/usr/bin/env python

"""
Global variables.
"""

import os
import geopandas
import shapely


# Global land cover used to subtract water from convex hull ranges.
LANDCOVER_FILE = os.path.join(
	os.path.dirname(os.path.dirname(__file__)), 
	"geojson",
	"land-cover.json",
)
LAND = shapely.geometry.MultiPolygon(
	geopandas.read_file(LANDCOVER_FILE).geometry.tolist()
)

# Colors for folium icons.
COLORS = ['blue', 
'green', 
'purple', 
'black', 
'darkblue', 
'darkgreen', 
'darkpurple', 
'lightblue', 
'lightgreen'
] 
OUTLIERS = ['red',
'gray', 
'beige', 
'white'
'pink', 
'orange', 
'darkred', 
'lightred', 
'lightgray'
]