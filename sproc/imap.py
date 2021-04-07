#!/usr/env/bin python

"""
Draw maps with folium
"""

import pandas as pd
import os
import geopandas as gpd
import folium
from sproc.globals import COLORS, OUTLIERS


# Make dataframes have wider columns for neatness.
pd.set_option("max_colwidth", 14)


class IMap:
    """
    Parameters:
    ------------
    location: Tuple[Float,Float]
        LatLong Point as center of the map.
    zoom_start: 
    """

    def __init__(self, json_files):

        # Differentiate between string filepath (ex: from jsonify.GeographicRange) or list of filepaths.
        if type(json_files) == str:
            self.json_files = [idx for idx in json_files.split(" ")]
        elif type(json_files) == list:
            self.json_files = json_files

        # Other variables.
        self.names = [os.path.basename(self.json_files[idx]).rsplit(".json")[0] for idx in range(len(self.json_files))]
        self.data = [gpd.read_file(self.json_files[idx]) for idx in range(len(self.json_files))]
        self.imap = None

        # Run internal functions.
        self._get_base_imap()
        self._add_poly()
        self._add_points()
        self._add_outlier_points()
        self.imap.add_child(folium.LayerControl())


    # TODO: in the future, consider best approach to allowing custom range merging.  Maybe at file level?
    # Adding points here might require resetting the whole polygon from jsonify module.
    def add_geojson(self, json_file):
        """
        Add GeoJSON data from another sproc GeoJSON file to this map.
        This can be used to merge together bounds and points from two
        or more species into a single polygon and point collection.
        """

        self.json_file = json_file
        self.name = os.path.basename(self.json_file).rsplit(".json")[0]
        self.data = gpd.read_file(json_file)

        # self._add_poly()
        self._add_points()
        # self._add_outlier_points()

        # refit the bounds
        # ...


    def _get_base_imap(self):
        """
        Load a basemap.
        """
        # Create the baselayer map.
        self.imap = folium.Map()
        # tiles='Stamen Terrain'
        # tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.png',
        # attr="IGN",


    def _add_poly(self):
        """
        Adds a MultiPolygon for the geographic range on its own layer.
        """

        # Iterate over GeoJSON files.
        for idx in range(len(self.json_files)):

            # Make a layer for the polygon.
            layer_poly = folium.FeatureGroup(name = f"{self.names[idx]} bounds")
        
            # Add the polygon to this layer.
            layer_poly.add_child(
                folium.GeoJson(
                    data = self.data[idx][self.data[idx]['type'] == "geographic_range"])
            )

            # Add this layer to the map.
            self.imap.add_child(layer_poly)
            # self.imap.fit_bounds(layer_poly.get_bounds())

        # Add lat/long popover function.
        # self.imap.add_child(folium.LatLngPopup())


    def _add_points(self):
        """
        Adds markers for occurrence points on a separate layer.
        """

        # Iterate over GeoJSON files.
        for idx in range(len(self.json_files)):

            # Make a layer for points.
            layer_points = folium.FeatureGroup(name = f"{self.names[idx]} occurrences")

            # Get points as markers.
            mask1 = self.data[idx]['type'] == "occurrence"
            mask2 = self.data[idx]['outlier'] == 'false'
            markers = folium.GeoJson(
                data = self.data[idx][mask1 & mask2],
                popup = folium.GeoJsonPopup(fields = ("record",), aliases = ("",)),
                marker = folium.Marker(
                    icon = folium.Icon(color = COLORS[idx])
                )
            )

            # Add markers to layer.
            layer_points.add_child(markers)
        
            # Add this layer to the map.
            self.imap.add_child(layer_points)


    def _add_outlier_points(self):
        """
        Adds outliers as points in red color.
        """

        # Iterate over GeoJSON files.
        for idx in range(len(self.json_files)):

            # Skip if there are no outliers.
            if all(self.data[idx][self.data[idx]['type'] == 'occurrence'].outlier == "false"):
                pass 

            # Make a layer for outliers.
            layer_outliers = folium.FeatureGroup(name = f"{self.names[idx]} outliers")

            # Get outliers as markers.
            mask1 = self.data[idx]['type'] == "occurrence"
            mask2 = self.data[idx]['outlier'] == 'true'
            markers = folium.GeoJson(
                data = self.data[idx][mask1 & mask2],
                popup = folium.GeoJsonPopup(fields = ("record",), aliases = ("",)),
                marker = folium.Marker(
                    icon = folium.Icon(color = OUTLIERS[idx], icon = "trash")
                )
            )

            # Add outliers to layer.
            layer_outliers.add_child(markers)
        
            # Add layer to map.
            self.imap.add_child(layer_outliers)