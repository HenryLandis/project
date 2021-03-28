#!/usr/env/bin python

"""
Draw maps with folium
"""

import os
import folium
import geopandas


class Map:
    """
    Parameters:
    ------------
    location: Tuple[Float,Float]
        LatLong Point as center of the map.
    zoom_start: 
    """
    def __init__(self, json_file):
        self.json_file = json_file
        self.name = os.path.basename(self.json_file).rsplit(".json")[0]
        self.data = geopandas.read_file(json_file)
        self.imap = None

        self._get_base_imap()
        self._add_poly()
        self._add_points()
        self._add_outlier_points()
        self.imap.add_child(folium.LayerControl())


    def _get_base_imap(self):
        """
        Load a basemap 
        """
        # create the baselayer map
        self.imap = folium.Map()
        # tiles='Stamen Terrain'
        # tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.png',
        # attr="IGN",


    def _add_poly(self):
        """
        Adds a MultiPolygon for the geographic range on its own layer
        """
        # make a layer for the polygon shape
        layer_poly = folium.FeatureGroup(name=f"Range: {self.name}")
        
        # add the polygon to this layer
        layer_poly.add_child(
            folium.GeoJson(
                data=self.data[self.data['type']=="geographic_range"])
        )

        # add this layer to the map
        self.imap.add_child(layer_poly)
        self.imap.fit_bounds(layer_poly.get_bounds())


    def _add_points(self):
        """
        Adds markers for occurrence points on a separate layer
        """
        # make a layer for points
        layer_points = folium.FeatureGroup(name="Occurrences")

        # get points as markers
        mask1 = self.data['type'] == "occurrence"
        mask2 = self.data['outlier'] == 'false'
        markers = folium.GeoJson(
            data=self.data[mask1 & mask2],
            popup=folium.GeoJsonPopup(fields=("record",), aliases=("",)),
        )

        # add markers to layer
        layer_points.add_child(markers)
        
        # add this layer to the map
        self.imap.add_child(layer_points)


    def _add_outlier_points(self):
        """
        Adds outliers as Points in red color
        """
        # make a layer for points
        layer_outliers = folium.FeatureGroup(name="Outliers")

        # get points as markers
        mask1 = self.data['type'] == "occurrence"
        mask2 = self.data['outlier'] == 'true'
        markers = folium.GeoJson(
            data=self.data[mask1 & mask2],
            popup=folium.GeoJsonPopup(fields=("record",), aliases=("",)),
            marker=folium.Marker(
                icon=folium.Icon(color="red", icon="trash")
            )
        )

        # add markers to layer
        layer_outliers.add_child(markers)
        
        # add this layer to the map
        self.imap.add_child(layer_outliers)





def draw_map(location=[40., 280.], zoom_start=4):

    
    # this is the layer that will hold all the points
    layer = folium.FeatureGroup(name='Your layer with Markers', control=True, show=False)

    # load the GEOJSON, but don't add it to anything
    geoj = folium.GeoJson('../geojson/Quercus_alba')
   
    
    # iterate over GEOJSON features, pull out point coordinates, 
    # make Markers and add to layer
    for feature in geoj.data['features']:
        if feature['geometry']['type'] == 'Point':
            
            tool_tip_text = '<pre>\n'

            for prop in feature['properties']:
                tool_tip_text = f"{tool_tip_text}{prop}: {feature['properties']['prop']}\n"
                #tool_tip_text + str(p) + ': ' + str(feature['properties'][p]) + '\n'

            tool_tip_text = tool_tip_text + '\n</pre>'

            tool_tip = folium.Tooltip(tool_tip_text)

            folium.Marker(
                location=list(reversed(feature['geometry']['coordinates'])),
                icon=folium.Icon(
                    icon_color='#ff033e',
                    icon='certificate',
                    prefix='fa'),
                tooltip=tool_tip
             ).add_to(layer)
    
    layer.add_to(fmap)  
    
    return fmap